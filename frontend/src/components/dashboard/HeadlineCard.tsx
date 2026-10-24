import { Alert, Button, Card, Empty, Skeleton, Typography } from "antd";
import type { ReactNode } from "react";
import { Link } from "react-router-dom";

interface HeadlineCardProps {
  title: string;
  value: ReactNode;
  caption: ReactNode;
  linkPath?: string;
  loading?: boolean;
  error?: string;
  emptyMessage?: string;
  onRetry?: () => void;
}

export default function HeadlineCard({
  title, value, caption, linkPath, loading = false, error, emptyMessage, onRetry,
}: HeadlineCardProps) {
  return (
    <Card
      role="region"
      aria-label={title}
      title={linkPath ? <Link to={linkPath}>{title}</Link> : title}
      style={{ height: "100%" }}
    >
      {loading ? (
        <div aria-label={`Loading ${title}`}><Skeleton active paragraph={false} /></div>
      ) : error ? (
        <Alert
          type="error"
          showIcon
          message={error}
          action={<Button onClick={onRetry}>Retry</Button>}
        />
      ) : (
        <>
          <div style={{ marginBottom: 16 }}>{value}</div>
          <Typography.Paragraph type="secondary">{caption}</Typography.Paragraph>
          {emptyMessage && <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description={emptyMessage} />}
        </>
      )}
    </Card>
  );
}
