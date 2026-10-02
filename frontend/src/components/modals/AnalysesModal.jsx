import { ANALYSES } from '../../constants/analyses.js';
import Modal from './Modal.jsx';

export default function AnalysesModal({ loading, onSelect, onClose }) {
  return (
    <Modal title="Cross analyses MES × PLM × ERP" className="analysis-modal" onClose={onClose}>
      <p className="analysis-intro">
        Each analysis links the 3 files: actual operations (MES), parts (PLM) and teams (ERP).
      </p>
      <div className="analysis-grid">
        {ANALYSES.map((analysis) => (
          <button key={analysis.id} className="analysis-card" onClick={() => onSelect(analysis)} disabled={loading}>
            <span className="analysis-card-title">{analysis.title}</span>
            <span className="analysis-card-desc">{analysis.description}</span>
            <span className="analysis-tags">
              {analysis.sources.map((source) => (
                <span key={source} className="analysis-tag">
                  {source}
                </span>
              ))}
            </span>
          </button>
        ))}
      </div>
      <div className="modal-actions" style={{ marginTop: '20px' }}>
        <button className="modal-btn modal-btn-secondary" onClick={onClose}>
          Close
        </button>
      </div>
    </Modal>
  );
}
