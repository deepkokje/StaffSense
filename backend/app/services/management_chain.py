from collections.abc import Callable


def detect_management_cycle(
    employee_id: int | None,
    new_manager_id: int | None,
    get_manager_id: Callable[[int], int | None],
) -> bool:
    visited = set() if employee_id is None else {employee_id}
    current = new_manager_id
    while current is not None:
        if current in visited:
            return True
        visited.add(current)
        current = get_manager_id(current)
    return False
