import { Home, ListChecks, Plane } from 'lucide-react';
import { ANALYSES, REPORTS } from '../../constants/analyses.js';
import FileListItem from './FileListItem.jsx';

function NavItem({ icon, label, active, disabled, badge, onClick }) {
  const Icon = icon;
  return (
    <button className={`nav-item ${active ? 'active' : ''}`} onClick={onClick} disabled={disabled} title={label}>
      <Icon size={16} strokeWidth={1.8} />
      <span className="nav-label">{label}</span>
      {badge && <span className="nav-badge">{badge}</span>}
    </button>
  );
}

/** Left navigation: home, standard reports, cross analyses and uploaded documents. */
export default function NavSidebar({ isOpen, view, loading, files, selectedFile, actions, onSelectFile }) {
  const isActive = (id) => view?.id === id;

  return (
    <nav className={`nav ${isOpen ? 'open' : 'closed'}`}>
      <div className="nav-brand">
        <span className="nav-logo">
          <Plane size={18} />
        </span>
        <div>
          <div className="nav-brand-name">Airplus</div>
          <div className="nav-brand-sub">Production analytics</div>
        </div>
      </div>

      <div className="nav-scroll">
        <NavItem icon={Home} label="Overview" active={!view} onClick={actions.goHome} />

        <div className="nav-section">Reports</div>
        {REPORTS.map((r) => (
          <NavItem
            key={r.id}
            icon={r.icon}
            label={r.title}
            active={isActive(r.id)}
            disabled={loading}
            onClick={actions[r.action]}
          />
        ))}
        <NavItem
          icon={ListChecks}
          label="Step details"
          active={isActive('step-details')}
          onClick={actions.toggleQuickAccess}
        />

        <div className="nav-section">Cross analyses</div>
        {ANALYSES.map((a) => (
          <NavItem
            key={a.id}
            icon={a.icon}
            label={a.title}
            badge={a.isNew ? 'New' : null}
            active={isActive(`analysis:${a.id}`)}
            disabled={loading}
            onClick={() => actions.analysis(a)}
          />
        ))}

        <div className="nav-section">
          Documents <span className="nav-count">{files.length}</span>
        </div>
        {files.length === 0 ? (
          <div className="nav-empty">No files</div>
        ) : (
          files.map((file) => (
            <FileListItem key={file.id} file={file} selected={selectedFile?.id === file.id} onSelect={onSelectFile} />
          ))
        )}
      </div>
    </nav>
  );
}
