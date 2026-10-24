import { Button, Card, Col, Row, Statistic } from "antd";

import type { BandStatusFilter, BandSummary } from "../api/types";

interface BandSummaryCardsProps {
  summary: BandSummary;
  status?: BandStatusFilter;
  onStatusChange: (status: BandStatusFilter | undefined) => void;
}

const SUMMARY_CARDS: { key: keyof BandSummary; label: string; filter?: BandStatusFilter }[] = [
  { key: "below_min", label: "Below min", filter: "below_min" },
  { key: "within_band", label: "Within band" },
  { key: "above_max", label: "Above max", filter: "above_max" },
  { key: "no_band", label: "No band" },
];

export default function BandSummaryCards({
  summary, status, onStatusChange,
}: BandSummaryCardsProps) {
  return (
    <Row gutter={[16, 16]}>
      {SUMMARY_CARDS.map(({ key, label, filter }) => (
        <Col xs={24} sm={12} lg={6} key={key}>
          <Card>
            {filter ? (
              <Button
                block
                type={status === filter ? "primary" : "text"}
                aria-label={label}
                aria-pressed={status === filter}
                style={{ height: "auto" }}
                onClick={() => onStatusChange(status === filter ? undefined : filter)}
              >
                <Statistic title={label} value={summary[key]} />
              </Button>
            ) : <Statistic title={label} value={summary[key]} />}
          </Card>
        </Col>
      ))}
    </Row>
  );
}
