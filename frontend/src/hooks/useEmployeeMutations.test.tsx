import { fireEvent, screen, waitFor } from "@testing-library/react";
import { expect, test, vi } from "vitest";
import { Button } from "antd";

import { fetchSalaryHistory, updateEmployee } from "../api/employees";
import { makeEmployee } from "../test/factories";
import { renderWithQueryClient } from "../test/renderWithQueryClient";
import { makeSalaryHistoryResponse } from "../test/salaryHistoryFactories";
import { useUpdateEmployee } from "./useEmployeeMutations";
import { useSalaryHistoryQuery } from "./useSalaryHistoryQuery";
import SalaryHistoryDrawer from "../components/SalaryHistoryDrawer";

vi.mock("../api/employees", () => ({
  fetchSalaryHistory: vi.fn(), updateEmployee: vi.fn(),
}));

function ActiveHistoryWithEdit() {
  const employee = makeEmployee({ currency: "USD" });
  const history = useSalaryHistoryQuery(employee.id);
  const update = useUpdateEmployee();
  const { id, salary_usd_minor: _usd, last_raise_date: _raise, ...editable } = employee;
  return (
    <>
      <Button
        disabled={!history.isSuccess}
        onClick={() => update.mutate({ id, data: { ...editable, salary_minor: 110000 } })}
      >Submit salary edit</Button>
      <SalaryHistoryDrawer employee={employee} onClose={() => undefined} />
    </>
  );
}

test("a successful salary edit refetches active history immediately without reopening", async () => {
  vi.mocked(fetchSalaryHistory).mockReset()
    .mockResolvedValueOnce(makeSalaryHistoryResponse([]))
    .mockResolvedValue(makeSalaryHistoryResponse());
  vi.mocked(updateEmployee).mockReset().mockResolvedValue(makeEmployee({ salary_minor: 110000 }));
  renderWithQueryClient(<ActiveHistoryWithEdit />);
  await screen.findByText("No salary changes recorded");
  expect(fetchSalaryHistory).toHaveBeenCalledTimes(1);
  fireEvent.click(screen.getByText("Submit salary edit"));
  await waitFor(() => expect(updateEmployee).toHaveBeenCalledWith(
    1, expect.objectContaining({ salary_minor: 110000 }),
  ));
  expect(await screen.findByText("+$100.00 (10.00%)")).toBeInTheDocument();
  expect(fetchSalaryHistory).toHaveBeenCalledTimes(2);
});
