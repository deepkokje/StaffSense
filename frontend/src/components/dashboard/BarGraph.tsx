import { Space, Typography } from "antd";

export interface BarGraphItem {
  label: string;
  value: number;
  displayValue: string;
  color: string;
}

interface BarGraphProps {
  label: string;
  items: readonly BarGraphItem[];
  summary?: string;
}

const GRAPH_WIDTH = 1_000;
const BAR_HEIGHT = 16;
const MIN_VISIBLE_WIDTH = 2;

export default function BarGraph({ label, items, summary }: BarGraphProps) {
  const maximum = items.reduce((largest, item) => Math.max(largest, item.value), 0);

  return (
    <Space
      role="group"
      aria-label={label}
      direction="vertical"
      size="middle"
      style={{ width: "100%" }}
    >
      {summary && <Typography.Text strong>{summary}</Typography.Text>}
      {items.map((item) => {
        // Integer scaling controls geometry only; displayed API amounts remain unchanged.
        const width = maximum === 0 || item.value === 0 ? 0 : Math.max(
          MIN_VISIBLE_WIDTH,
          Number(BigInt(item.value) * BigInt(GRAPH_WIDTH) / BigInt(maximum)),
        );
        return (
          <div key={item.label}>
            <div style={{ display: "flex", justifyContent: "space-between", gap: 12 }}>
              <Typography.Text>{item.label}</Typography.Text>
              <Typography.Text strong>{item.displayValue}</Typography.Text>
            </div>
            <svg
              role="img"
              aria-label={`${item.label}: ${item.displayValue}`}
              viewBox={`0 0 ${GRAPH_WIDTH} ${BAR_HEIGHT}`}
              preserveAspectRatio="none"
              style={{ display: "block", width: "100%", height: BAR_HEIGHT, marginTop: 4 }}
            >
              <rect width={GRAPH_WIDTH} height={BAR_HEIGHT} rx={4} fill="#f0f0f0" />
              <rect width={width} height={BAR_HEIGHT} rx={4} fill={item.color} />
            </svg>
          </div>
        );
      })}
      <Typography.Text type="secondary">
        Bar lengths use a separate scale in each card.
      </Typography.Text>
    </Space>
  );
}
