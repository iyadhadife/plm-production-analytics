import { AlertCircle, CheckCircle } from 'lucide-react';

const ICONS = {
  error: <AlertCircle size={14} />,
  success: <CheckCircle size={14} />,
};

export default function StatusBadge({ status }) {
  if (!status.message) return null;
  return (
    <div className={`status-badge ${status.type}`}>
      {ICONS[status.type] ?? null}
      {status.message}
    </div>
  );
}
