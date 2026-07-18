import './status-message.css';

type StatusType = 'idle' | 'loading' | 'success' | 'error';

interface StatusMessageProps {
  status: StatusType;
  message: string;
}

export function StatusMessage({ status, message }: StatusMessageProps) {
  if (status === 'idle' || status === 'loading') {
    return null;
  }

  return (
    <div className={`status-message ${status}`}>
      {message}
    </div>
  );
}