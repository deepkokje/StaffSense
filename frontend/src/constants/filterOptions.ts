import type { EmployeeStatus, Gender } from "../api/types";

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
