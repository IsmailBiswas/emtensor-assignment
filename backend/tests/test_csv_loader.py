from datetime import date
from pathlib import Path

import pytest

from app.adapters.csv_loader import CsvProjectDataLoader
from app.domain.parsing import parse_optional_date

REPO_DATA = Path(__file__).resolve().parents[2] / "data"


@pytest.fixture(scope="module")
def dataset():
    loader = CsvProjectDataLoader(REPO_DATA, as_of=date(2026, 9, 15))
    return loader.load()


def test_loads_expected_row_counts(dataset) -> None:
    counts = dataset.summary_counts()
    assert counts["departments"] == 8
    assert counts["researchers"] == 61
    assert counts["funding_tranches"] == 4
    assert counts["milestones"] == 6
    assert counts["work_packages"] == 58
    assert counts["components"] == 315
    assert counts["timesheets"] > 2000


def test_indexes_and_adjacency_lists(dataset) -> None:
    assert "PWR" in dataset.departments_by_id
    assert "R001" in dataset.researchers_by_id
    assert "T3" in dataset.tranches_by_id
    assert "M4" in dataset.milestones_by_id

    assert "SEN-04" in dataset.task_successors["PWR-05"]
    assert "PWR-05" in dataset.task_predecessors["SEN-04"]

    assert "PWS-SOL-R1" in dataset.component_depends_on["FLD-GAU-R1"]
    assert "FLD-GAU-R1" in dataset.component_required_by["PWS-SOL-R1"]

    assert dataset.tranche_by_condition_milestone["M4"].tranche_id == "T3"
    assert dataset.milestone_by_released_tranche["T3"].milestone_id == "M4"


def test_messy_date_parsing_preserved() -> None:
    assert parse_optional_date("2026-09-15") == date(2026, 9, 15)
    assert parse_optional_date("08/07/2026") == date(2026, 7, 8)
    assert parse_optional_date("") is None


def test_milestone_linked_tasks_split(dataset) -> None:
    m4 = dataset.milestones_by_id["M4"]
    assert m4.linked_task_ids == ["SEN-05", "SEN-07", "ENC-06"]
    assert m4.releases_tranche_id == "T3"

    m3 = dataset.milestones_by_id["M3"]
    assert m3.releases_tranche_id is None
