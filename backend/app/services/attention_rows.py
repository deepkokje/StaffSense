from typing import Protocol

from app.services.benchmarks import BenchmarkSalaryRow


class AttentionSalaryRow(BenchmarkSalaryRow, Protocol):
    @property
    def employee_id(self) -> int: ...

    @property
    def name(self) -> str: ...

    @property
    def department(self) -> str: ...
