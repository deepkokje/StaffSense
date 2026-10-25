import pytest

from app.services.management_chain import detect_management_cycle


@pytest.mark.parametrize(
    ("employee_id", "manager_id", "chain", "expected"),
    [
        (1, None, {}, False),
        (1, 2, {2: 3, 3: None}, False),
        (1, 1, {}, True),
        (3, 1, {1: 2, 2: 3}, True),
        (1, 4, {4: None}, False),
        (1, 2, {2: 3, 3: 2}, True),
    ],
)
def test_detects_management_cycles(
    employee_id: int,
    manager_id: int | None,
    chain: dict[int, int | None],
    expected: bool,
) -> None:
    assert detect_management_cycle(employee_id, manager_id, chain.get) is expected
