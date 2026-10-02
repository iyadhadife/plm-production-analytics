import { Maximize2 } from 'lucide-react';

export default function ResultBanner({ onFullscreen, onClose }) {
  return (
    <div className="result-banner">
      <h3 className="result-title">📊 Result</h3>
      <div className="result-actions">
        <button onClick={onFullscreen} className="result-icon-btn" title="Show fullscreen">
          <Maximize2 size={18} />
        </button>
        <button onClick={onClose} className="result-icon-btn close" title="Close">
          ✖
        </button>
      </div>
    </div>
  );
}
