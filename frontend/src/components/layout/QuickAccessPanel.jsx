import { X } from 'lucide-react';
import { useState } from 'react';

/** Right sidebar: pick an assembly step and open its details report. */
export default function QuickAccessPanel({ isOpen, steps, loading, onClose, onShowStepDetails }) {
  const [step, setStep] = useState('');

  return (
    <div className={`sidebar-right ${isOpen ? 'open' : 'closed'}`}>
      <div className="sidebar-right-header">
        <h2 className="sidebar-right-title">Quick access</h2>
        <button onClick={onClose} className="sidebar-close-btn" title="Close">
          <X size={18} />
        </button>
      </div>

      <div className="sidebar-right-content">
        <div className="step-picker">
          <label htmlFor="step-select">Assembly step</label>
          <select id="step-select" value={step} onChange={(e) => setStep(e.target.value)} className="step-dropdown">
            <option value="">-- Select a step --</option>
            {steps.map((name) => (
              <option key={name} value={name}>
                {name}
              </option>
            ))}
          </select>
          <button
            onClick={() => onShowStepDetails(step)}
            className="sidebar-action-btn"
            disabled={loading || !step}
            title={step ? '' : 'Please select a step'}
          >
            {loading ? 'Loading...' : 'Show step details'}
          </button>
        </div>
      </div>
    </div>
  );
}
