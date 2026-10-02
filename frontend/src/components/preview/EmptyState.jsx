import { Upload } from 'lucide-react';

export default function EmptyState() {
  return (
    <div className="empty-placeholder">
      <div className="empty-icon-circle">
        <Upload size={40} />
      </div>
      <h3>No file selected</h3>
      <p>Select a document or upload a new one.</p>
    </div>
  );
}
