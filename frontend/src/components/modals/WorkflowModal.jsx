import { useState } from 'react';
import Modal from './Modal.jsx';

const DEFAULT_MAX_NODES = 50;

/** Options of the Sankey workflow report: optional step filter and node limit. */
export default function WorkflowModal({ steps, loading, onSubmit, onClose }) {
  const [step, setStep] = useState('');
  const [maxNodes, setMaxNodes] = useState(DEFAULT_MAX_NODES);

  return (
    <Modal title="Sankey workflow settings" onClose={onClose}>
      <div className="modal-body">
        <div className="form-group">
          <label>Step (optional — leave empty for all steps)</label>
          <select value={step} onChange={(e) => setStep(e.target.value)}>
            <option value="">-- All steps --</option>
            {steps.map((name) => (
              <option key={name} value={name}>
                {name}
              </option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label>Maximum number of nodes per level</label>
          <input
            type="number"
            min="5"
            max="200"
            value={maxNodes}
            onChange={(e) => setMaxNodes(parseInt(e.target.value, 10) || DEFAULT_MAX_NODES)}
          />
        </div>
      </div>
      <div className="modal-actions">
        <button className="modal-btn modal-btn-secondary" onClick={onClose}>
          Cancel
        </button>
        <button className="modal-btn modal-btn-primary" onClick={() => onSubmit(step, maxNodes)} disabled={loading}>
          {loading ? 'Loading...' : 'Show'}
        </button>
      </div>
    </Modal>
  );
}
