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

export type BandStatus = "below_min" | "within_band" | "above_max";
export type BandStatusFilter = Exclude<BandStatus, "within_band">;
export type OutlierDirection = "above" | "below";

export interface BandSummary {
  below_min: number;
  within_band: number;
  above_max: number;
  no_band: number;
}

export interface AttentionEmployee {
  employee_id: number;
  name: string;
  title: string;
  level: number;
  country: string;
  currency: string;
  salary_minor: number;
}

export interface FlaggedEmployee extends AttentionEmployee {
  department: string;
  band_min_minor: number;
  band_mid_minor: number;
  band_max_minor: number;
  compa_ratio_permille: number;
  status: BandStatus;
  gap_to_band_minor: number;
}

export interface Outlier extends AttentionEmployee {
  group_median_minor: number;
  group_headcount: number;
  deviation_permille: number;
  direction: OutlierDirection;
}

export interface AttentionPageQuery {
  page: number;
  page_size: number;
}

export interface PeerFilters {
  country?: readonly string[];
  title?: readonly string[];
  level?: readonly number[];
}

export interface BandsQuery extends AttentionPageQuery, PeerFilters {
  department?: readonly string[];
  status?: BandStatusFilter;
}

export interface OutliersQuery extends AttentionPageQuery, PeerFilters {
  direction?: OutlierDirection;
}

export interface BandsResponse extends AttentionPageQuery {
  summary: BandSummary;
  items: FlaggedEmployee[];
  total: number;
}

export interface OutliersResponse extends AttentionPageQuery {
  items: Outlier[];
  total: number;
}
