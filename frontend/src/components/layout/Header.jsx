import { Menu } from 'lucide-react';
import ReportToolbar from './ReportToolbar.jsx';
import StatusBadge from './StatusBadge.jsx';
import UploadButton from './UploadButton.jsx';

export default function Header({ title, status, loading, actions, isQuickAccessOpen, onToggleSidebar, onUpload }) {
  return (
    <header className="top-header">
      <div className="header-left">
        <button onClick={onToggleSidebar} className="icon-btn" title="Toggle file list">
          <Menu size={20} />
        </button>
        <h1 className="page-title">{title}</h1>
        <ReportToolbar loading={loading} actions={actions} isQuickAccessOpen={isQuickAccessOpen} />
      </div>

      <div className="header-right">
        <StatusBadge status={status} />
        <UploadButton onFileSelected={onUpload} />
      </div>
    </header>
  );
}
