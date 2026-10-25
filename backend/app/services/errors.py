class EmployeeError(ValueError):
    pass


class EmployeeNotFound(EmployeeError):
    pass


class DuplicateEmail(EmployeeError):
    pass


class InvalidManager(EmployeeError):
    pass


class UnsupportedChange(EmployeeError):
    pass


class HasDirectReports(EmployeeError):
    pass


class MissingFxRate(EmployeeError):
    pass
