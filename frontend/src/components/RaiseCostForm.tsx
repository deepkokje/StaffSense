import { Button, Form, Input, Select } from "antd";

import type { RaiseCostQuery } from "../api/types";
import { COUNTRY_OPTIONS, DEPARTMENT_OPTIONS } from "../constants/filterOptions";
import { percentToBasisPoints } from "../lib/percentToBasisPoints";

interface RaiseFormValues {
  department: string;
  percent: string;
  country?: string;
}

interface RaiseCostFormProps {
  onCalculate: (query: RaiseCostQuery) => void;
  loading: boolean;
}

export default function RaiseCostForm({ onCalculate, loading }: RaiseCostFormProps) {
  const [form] = Form.useForm<RaiseFormValues>();

  function submit(values: RaiseFormValues) {
    const parsed = percentToBasisPoints(values.percent);
    if (!parsed.ok) {
      form.setFields([{ name: "percent", errors: [parsed.reason] }]);
      return;
    }
    onCalculate({
      department: values.department,
      raise_bp: parsed.basisPoints,
      ...(values.country === undefined ? {} : { country: values.country }),
    });
  }

  return (
    <Form<RaiseFormValues> form={form} layout="vertical" onFinish={submit}>
      <Form.Item
        name="department"
        label="Department"
        rules={[{ required: true, message: "Choose a department." }]}
      >
        <Select
          virtual={false}
          placeholder="Choose department"
          options={DEPARTMENT_OPTIONS.map((value) => ({ label: value, value }))}
        />
      </Form.Item>
      <Form.Item
        name="percent"
        label="Percent"
        rules={[{
          validator: (_rule: unknown, value: string | undefined) => {
            const parsed = percentToBasisPoints(value ?? "");
            return parsed.ok ? Promise.resolve() : Promise.reject(new Error(parsed.reason));
          },
        }]}
      >
        <Input inputMode="decimal" placeholder="For example, 5 or 2.5" />
      </Form.Item>
      <Form.Item name="country" label="Country">
        <Select
          aria-label="Raise country"
          virtual={false}
          allowClear
          placeholder="All countries"
          options={COUNTRY_OPTIONS.map((value) => ({ label: value, value }))}
        />
      </Form.Item>
      <Button type="primary" htmlType="submit" loading={loading}>Calculate</Button>
    </Form>
  );
}
