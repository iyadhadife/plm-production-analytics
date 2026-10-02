import { Minimize2 } from 'lucide-react';
import ReportFrame from './ReportFrame.jsx';

export default function FullscreenReport({ html, onExit }) {
  return (
    <div className="fullscreen">
      <div className="fullscreen-bar">
        <button onClick={onExit} className="exit-fullscreen-btn" title="Exit fullscreen">
          <Minimize2 size={16} />
          Exit
        </button>
      </div>
      <div className="fullscreen-body">
        <ReportFrame html={html} title="Fullscreen report" />
      </div>
    </div>
  );
}
