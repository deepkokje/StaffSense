import type { EmployeeStatus, EmploymentType, Gender } from "../api/types";

export const CURRENCY_EXPONENTS: Readonly<Record<string, number>> = {
  USD: 2, EUR: 2, GBP: 2, INR: 2, JPY: 0, CAD: 2, AUD: 2, SGD: 2,
};
export const CURRENCY_OPTIONS = Object.keys(CURRENCY_EXPONENTS);
export const EMPLOYMENT_TYPE_OPTIONS: EmploymentType[] = ["FULL_TIME", "PART_TIME", "CONTRACT"];

// These fixed options will come from the API later.
export const COUNTRY_OPTIONS = ["US", "GB", "DE", "IN", "SG", "CA", "AU", "JP"];
export const DEPARTMENT_OPTIONS = [
  "Engineering",
  "Data",
  "Product",
  "HR",
  "Finance",
  "Sales",
  "Support",
];
export const LEVEL_OPTIONS = [1, 2, 3, 4, 5, 6];
export const STATUS_OPTIONS: EmployeeStatus[] = ["ACTIVE", "ON_LEAVE", "TERMINATED"];
export const GENDER_OPTIONS: Gender[] = ["FEMALE", "MALE", "OTHER", "UNDISCLOSED"];
export const TITLE_OPTIONS = [
  "Software Engineer",
  "QA Engineer",
  "Data Analyst",
  "Data Scientist",
  "Product Manager",
  "Designer",
  "HR Specialist",
  "Recruiter",
  "Accountant",
  "Financial Analyst",
  "Sales Executive",
  "Customer Support Specialist",
];
