import { Alert, Button } from "antd";

interface ErrorBannerProps {
  title?: string;
  message: string;
  onRetry: () => void;
  retrying: boolean;
}

export default function ErrorBanner({
  title = "Unable to load employees",
  message,
  onRetry,
  retrying,
}: ErrorBannerProps) {
  return (
    <Alert
      action={
        <Button loading={retrying} onClick={onRetry}>
          Retry
        </Button>
      }
      message={title}
      description={message}
      showIcon
      type="error"
    />
  );
}
