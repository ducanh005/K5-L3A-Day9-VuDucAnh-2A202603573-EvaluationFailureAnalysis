"""Additional M5-M7 tests for hidden integrity traps (duplicate rows, evaluator_failures, slice tampering)."""
from __future__ import annotations

import copy

import pytest

from lab9 import gate

pytestmark = pytest.mark.student

ROWS = [
    {"item_id": f"E-{i:03d}", "seed": s, "pass_rate": True, "slices": ["money_movement"] if i < 2 else []}
    for i in range(4)
    for s in (1, 2)
]
SPEC = {
    "eval_set_version": "v2",
    "metrics": [{"id": "pass_rate", "kind": "capability", "blocking": True, "threshold": {"min": 0.85}}],
    "slices": [{"name": "money_movement", "metric": "pass_rate", "min": 0.95, "blocking": True}],
}


def _report(rows, metrics=None, failures=()):
    return {
        "manifest": {"eval_set_sha": "x", "items": 4, "seeds": [1, 2]},
        "rows": rows,
        "metrics": metrics if metrics is not None else {"pass_rate": 1.0},
        "evaluator_failures": list(failures),
    }


def test_integrity_flags_duplicate_row_with_unchanged_length():
    base = _report(copy.deepcopy(ROWS))
    dup = copy.deepcopy(ROWS[:-1]) + [copy.deepcopy(ROWS[0])]
    assert len(dup) == len(ROWS)
    assert gate.integrity_check(dup_rep := _report(dup), base, SPEC)
    assert any("duplicate" in p or "differs" in p for p in gate.integrity_check(dup_rep, base, SPEC))


def test_integrity_flags_evaluator_failures_even_when_metrics_green():
    base = _report(copy.deepcopy(ROWS))
    bad = _report(copy.deepcopy(ROWS), failures=["E-001@1:Grader:crashed"])
    problems = gate.integrity_check(bad, base, SPEC)
    assert any("evaluator_failures" in p for p in problems)


def test_integrity_flags_relabeled_slice_tags():
    base = _report(copy.deepcopy(ROWS))
    tampered = copy.deepcopy(ROWS)
    tampered[0]["slices"] = []
    problems = gate.integrity_check(_report(tampered), base, SPEC)
    assert any("slice tags changed" in p for p in problems)
