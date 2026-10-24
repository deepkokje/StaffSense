import { Tabs, Typography } from "antd";
import { useSearchParams } from "react-router-dom";

import BandsTab from "./attention/BandsTab";
import OutliersTab from "./attention/OutliersTab";

const BANDS_TAB = "bands";
const OUTLIERS_TAB = "outliers";
const TAB_PARAM = "tab";
const TAB_ITEMS = [
  { key: BANDS_TAB, label: "Outside band", children: <BandsTab /> },
  { key: OUTLIERS_TAB, label: "Outliers vs peers", children: <OutliersTab /> },
];

export default function AttentionPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const activeTab = searchParams.get(TAB_PARAM) === OUTLIERS_TAB ? OUTLIERS_TAB : BANDS_TAB;

  function changeTab(tab: string) {
    setSearchParams((current) => {
      const next = new URLSearchParams(current);
      next.set(TAB_PARAM, tab);
      return next;
    });
  }

  return (
    <>
      <Typography.Title level={1}>Needs attention</Typography.Title>
      <Tabs activeKey={activeTab} onChange={changeTab} items={TAB_ITEMS} destroyInactiveTabPane />
    </>
  );
}
