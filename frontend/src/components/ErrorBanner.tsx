import { Alert, Button } from "antd";

interface ErrorBannerProps {
  message: string;
  onRetry: () => void;
  retrying: boolean;
}

export default function ErrorBanner({ message, onRetry, retrying }: ErrorBannerProps) {
  return (
    <Alert
      action={
        <Button loading={retrying} onClick={onRetry}>
          Retry
        </Button>
      }
      message="Unable to load employees"
      description={message}
      showIcon
      type="error"
    />
  );
}
