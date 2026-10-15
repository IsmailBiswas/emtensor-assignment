from datetime import date
from pathlib import Path

from app.adapters.csv_loader import CsvProjectDataLoader
from app.services.anomalies import detect_anomalies

REPO_DATA = Path(__file__).resolve().parents[2] / "data"


def test_detects_core_rule_breaks() -> None:
    dataset = CsvProjectDataLoader(REPO_DATA, as_of=date(2026, 9, 15)).load()
    result = detect_anomalies(dataset)
    rules = {item.rule for item in result.items}
    assert "missing_purchase_order" in rules
    assert "po_overpaid" in rules
    assert "requester_equals_approver" in rules
    assert "task_dependency_order" in rules
    assert "component_dependency_install" in rules
    assert "milestone_self_report" in rules
    assert result.total > 20
