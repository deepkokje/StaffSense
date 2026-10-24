export type Gender = "FEMALE" | "MALE" | "OTHER" | "UNDISCLOSED";

export type EmploymentType = "FULL_TIME" | "PART_TIME" | "CONTRACT";

export type EmployeeStatus = "ACTIVE" | "ON_LEAVE" | "TERMINATED";

export type SortField =
  | "name"
  | "title"
  | "department"
  | "country"
  | "level"
  | "salary_usd_minor"
  | "hire_date";

export type SortDirection = "asc" | "desc";
export type EmployeeQueryValue =
  | string
  | number
  | boolean
  | readonly (string | number | boolean)[]
  | undefined;

export interface EmployeeOut {
  id: number;
  name: string;
  email: string;
  title: string;
  level: number;
  department: string;
  country: string;
  currency: string;
  salary_minor: number;
  salary_usd_minor: number;
  gender: Gender;
  employment_type: EmploymentType;
  hire_date: string;
  last_raise_date: string | null;
  status: EmployeeStatus;
  manager_id: number | null;
}

export interface EmployeePage {
  items: EmployeeOut[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface EmployeeQuery extends Record<string, EmployeeQueryValue> {
  page: number;
  page_size: number;
  q?: string;
  country?: readonly string[];
  department?: readonly string[];
  title?: readonly string[];
  level?: readonly number[];
  status?: readonly EmployeeStatus[];
  gender?: readonly Gender[];
  min_salary_usd_minor?: number;
  max_salary_usd_minor?: number;
  sort_by: SortField;
  sort_dir: SortDirection;
}

export interface BenchmarkStats {
  min: number;
  p25: number;
  median: number;
  p75: number;
  max: number;
}

export interface PeerGroupBenchmark {
  key: { title: string; level: number; country: string };
  currency: string;
  headcount: number;
  stats: BenchmarkStats | null;
  insufficient_data: boolean;
}

export interface BenchmarksResponse {
  items: PeerGroupBenchmark[];
}

export interface BenchmarksQuery {
  country?: readonly string[];
  title?: readonly string[];
  level?: readonly number[];
  include_insufficient: boolean;
}
