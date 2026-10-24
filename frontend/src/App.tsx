import { Layout } from "antd";

import EmployeesPage from "./pages/EmployeesPage";

const APP_NAME = "StaffSense";
const CONTENT_PADDING = 24;

export default function App() {
  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Layout.Header>
        <span style={{ color: "white" }}>{APP_NAME}</span>
      </Layout.Header>
      <Layout.Content style={{ padding: CONTENT_PADDING }}>
        <EmployeesPage />
      </Layout.Content>
    </Layout>
  );
}
