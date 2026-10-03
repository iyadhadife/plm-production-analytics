import { Maximize2, PanelLeft, X } from 'lucide-react';
import StatusBadge from './StatusBadge.jsx';
import UploadButton from './UploadButton.jsx';

export default function Header({ view, status, hasReport, onToggleSidebar, onUpload, onFullscreen, onClose }) {
  return (
    <header className="top-header">
      <div className="header-left">
        <button onClick={onToggleSidebar} className="icon-btn" title="Toggle navigation">
          <PanelLeft size={18} />
        </button>
        <div className="header-titles">
          <span className="header-eyebrow">{view ? view.subtitle : 'Dashboard'}</span>
          <h1 className="page-title">{view ? view.title : 'Production overview'}</h1>
        </div>
      </div>

      <div className="header-right">
        <StatusBadge status={status} />
        {hasReport && (
          <button onClick={onFullscreen} className="ghost-btn" title="Show fullscreen">
            <Maximize2 size={16} />
            <span>Fullscreen</span>
          </button>
        )}
        {view && (
          <button onClick={onClose} className="icon-btn" title="Close">
            <X size={18} />
          </button>
        )}
        <UploadButton onFileSelected={onUpload} />
      </div>
    </header>
  );
}
