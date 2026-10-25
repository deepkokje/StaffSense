import { useState } from "react";
import { Alert, Button, DatePicker, Drawer, Form, Input, InputNumber, Select, Tooltip } from "antd";
import dayjs from "dayjs";
import type { Dayjs } from "dayjs";

import { ApiError } from "../api/client";
import type { EmployeeInput, EmployeeOut } from "../api/types";
import {
  COUNTRY_OPTIONS, CURRENCY_OPTIONS, DEPARTMENT_OPTIONS, EMPLOYMENT_TYPE_OPTIONS,
  GENDER_OPTIONS, LEVEL_OPTIONS, STATUS_OPTIONS, TITLE_OPTIONS,
} from "../constants/filterOptions";
import { useCreateEmployee, useUpdateEmployee } from "../hooks/useEmployeeMutations";
import { formatMinorUnitsPlain } from "../lib/formatMinorUnitsPlain";
import { parseMoneyInput } from "../lib/parseMoneyInput";

const DATE_FORMAT = "YYYY-MM-DD";
const REQUIRED_RULE = { required: true, message: "This field is required." };
const DRAWER_WIDTH = 520;
const EMAIL_CONFLICT_STATUS = 409;

interface EmployeeFormDrawerProps {
  employee?: EmployeeOut;
  onClose: () => void;
}

type FormValues = Omit<EmployeeInput, "salary_minor" | "hire_date"> & {
  salary: string;
  hire_date: Dayjs;
};

function options(values: readonly (string | number)[]) {
  return values.map((value) => ({ label: String(value), value }));
}

export default function EmployeeFormDrawer({ employee, onClose }: EmployeeFormDrawerProps) {
  const [form] = Form.useForm<FormValues>();
  const [errorMessage, setErrorMessage] = useState<string>();
  const createMutation = useCreateEmployee();
  const updateMutation = useUpdateEmployee();
  const currency: string | undefined = Form.useWatch("currency", form);
  const isPending = createMutation.isPending || updateMutation.isPending;
  const initialValues: Partial<FormValues> = employee
    ? {
        name: employee.name, email: employee.email, title: employee.title,
        department: employee.department, country: employee.country, currency: employee.currency,
        level: employee.level, gender: employee.gender, employment_type: employee.employment_type,
        status: employee.status, manager_id: employee.manager_id,
        salary: formatMinorUnitsPlain(employee.salary_minor, employee.currency),
        hire_date: dayjs(employee.hire_date),
      }
    : { currency: "USD", gender: "UNDISCLOSED", employment_type: "FULL_TIME", status: "ACTIVE" };

  async function submit(values: FormValues) {
    const parsed = parseMoneyInput(values.salary, values.currency);
    if (!parsed.ok) {
      form.setFields([{ name: "salary", errors: [parsed.reason] }]);
      return;
    }
    setErrorMessage(undefined);
    const { salary: _salary, hire_date, ...fields } = values;
    const data: EmployeeInput = {
      ...fields, salary_minor: parsed.amountMinor, hire_date: hire_date.format(DATE_FORMAT),
      manager_id: values.manager_id ?? null,
    };
    try {
      if (employee) {
        await updateMutation.mutateAsync({ id: employee.id, data });
      } else {
        await createMutation.mutateAsync(data);
      }
      onClose();
    } catch (error) {
      if (error instanceof ApiError && error.status === EMAIL_CONFLICT_STATUS) {
        form.setFields([{ name: "email", errors: [error.message] }]);
      } else {
        setErrorMessage(error instanceof Error ? error.message : "Unable to save employee.");
      }
    }
  }

  return (
    <Drawer
      open title={employee ? "Edit employee" : "Add employee"} width={DRAWER_WIDTH}
      onClose={isPending ? undefined : onClose} maskClosable={!isPending} keyboard={!isPending}
    >
      {errorMessage && <Alert type="error" showIcon message={errorMessage} />}
      <Form<FormValues>
        form={form} layout="vertical" initialValues={initialValues}
        onFinish={(values) => void submit(values)} disabled={isPending}
      >
        <Form.Item name="name" label="Name" rules={[REQUIRED_RULE, { whitespace: true }]}>
          <Input maxLength={200} />
        </Form.Item>
        <Form.Item name="email" label="Email" rules={[REQUIRED_RULE]}>
          <Input />
        </Form.Item>
        <Form.Item name="title" label="Title" rules={[REQUIRED_RULE]}>
          <Select showSearch options={options(TITLE_OPTIONS)} />
        </Form.Item>
        <Form.Item name="department" label="Department" rules={[REQUIRED_RULE]}>
          <Select options={options(DEPARTMENT_OPTIONS)} />
        </Form.Item>
        <Form.Item name="country" label="Country" rules={[REQUIRED_RULE]}>
          <Select options={options(COUNTRY_OPTIONS)} />
        </Form.Item>
        <Tooltip title={employee ? "Currency cannot be changed" : undefined}>
          <div>
            <Form.Item name="currency" label="Currency" rules={[REQUIRED_RULE]}>
              <Select disabled={Boolean(employee)} options={options(CURRENCY_OPTIONS)} />
            </Form.Item>
          </div>
        </Tooltip>
        <Form.Item name="salary" label={`Salary (${currency ?? "USD"})`} rules={[REQUIRED_RULE]}>
          <Input inputMode="decimal" placeholder="1,50,000.00" />
        </Form.Item>
        <Form.Item name="level" label="Level" rules={[REQUIRED_RULE]}>
          <Select options={options(LEVEL_OPTIONS)} />
        </Form.Item>
        <Form.Item name="gender" label="Gender" rules={[REQUIRED_RULE]}>
          <Select options={options(GENDER_OPTIONS)} />
        </Form.Item>
        <Form.Item name="employment_type" label="Employment type" rules={[REQUIRED_RULE]}>
          <Select options={options(EMPLOYMENT_TYPE_OPTIONS)} />
        </Form.Item>
        <Form.Item name="status" label="Status" rules={[REQUIRED_RULE]}>
          <Select options={options(STATUS_OPTIONS)} />
        </Form.Item>
        <Form.Item name="hire_date" label="Hire date" rules={[REQUIRED_RULE]}>
          <DatePicker format={DATE_FORMAT} style={{ width: "100%" }} />
        </Form.Item>
        <Form.Item name="manager_id" label="Manager ID" rules={[{
          validator: (_rule, value: number | null | undefined) =>
            value == null || (Number.isSafeInteger(value) && value > 0)
              ? Promise.resolve()
              : Promise.reject(new Error("Enter a positive integer manager ID.")),
        }]}>
          <InputNumber min={1} precision={0} style={{ width: "100%" }} />
        </Form.Item>
        <Button type="primary" htmlType="submit" loading={isPending}>Save employee</Button>
      </Form>
    </Drawer>
  );
}
