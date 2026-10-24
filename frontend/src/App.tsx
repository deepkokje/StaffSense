import { Layout } from "antd";

import Dashboard from "./pages/Dashboard";

export default function App() {
  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Layout.Header>
        <span style={{ color: "white" }}>StaffSense</span>
      </Layout.Header>
      <Layout.Content style={{ padding: "24px" }}>
        <Dashboard />
      </Layout.Content>
    </Layout>
  );
}
