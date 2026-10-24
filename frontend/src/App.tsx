import { Layout, Menu } from "antd";
import { Link, Navigate, Route, Routes, useLocation } from "react-router-dom";

import { NAVIGATION_ITEMS } from "./constants/navigation";
import AttentionPage from "./pages/AttentionPage";
import BenchmarksPage from "./pages/BenchmarksPage";
import EmployeesPage from "./pages/EmployeesPage";
import WhatIfPage from "./pages/WhatIfPage";

const APP_NAME = "StaffSense";
const CONTENT_PADDING = 24;

export default function App() {
  const location = useLocation();
  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Layout.Header>
        <span style={{ color: "white" }}>{APP_NAME}</span>
      </Layout.Header>
      <Layout>
        <Layout.Sider breakpoint="lg" collapsedWidth={0}>
          <Menu
            theme="dark"
            mode="inline"
            selectedKeys={[location.pathname]}
            items={NAVIGATION_ITEMS.map((item) => ({
              key: item.path,
              label: <Link to={item.path}>{item.label}</Link>,
            }))}
          />
        </Layout.Sider>
        <Layout.Content style={{ padding: CONTENT_PADDING, minWidth: 0 }}>
          <Routes>
            <Route path="/" element={<Navigate to="/employees" replace />} />
            <Route path="/employees" element={<EmployeesPage />} />
            <Route path="/insights/benchmarks" element={<BenchmarksPage />} />
            <Route path="/insights/attention" element={<AttentionPage />} />
            <Route path="/insights/what-if" element={<WhatIfPage />} />
          </Routes>
        </Layout.Content>
      </Layout>
    </Layout>
  );
}
