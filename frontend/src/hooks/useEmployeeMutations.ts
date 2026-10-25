import { useMutation, useQueryClient } from "@tanstack/react-query";
import { message } from "antd";

import { createEmployee, deleteEmployee, updateEmployee } from "../api/employees";
import type { EmployeeInput } from "../api/types";
import { invalidateEmployeeData } from "../lib/invalidateEmployeeData";

export function useCreateEmployee() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: createEmployee,
    onSuccess: async () => {
      await invalidateEmployeeData(client);
      void message.success("Employee added.");
    },
  });
}

export function useUpdateEmployee() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: EmployeeInput }) => updateEmployee(id, data),
    onSuccess: async () => {
      await invalidateEmployeeData(client);
      void message.success("Employee updated.");
    },
  });
}

export function useDeleteEmployee() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: deleteEmployee,
    onSuccess: async () => {
      await invalidateEmployeeData(client);
      void message.success("Employee deleted.");
    },
    onError: (error) => {
      void message.error(error.message);
    },
  });
}
