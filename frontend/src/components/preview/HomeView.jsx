import { ArrowUpRight } from 'lucide-react';
import { ANALYSES, REPORTS } from '../../constants/analyses.js';

const SOURCES = [
  { id: 'MES', name: 'Execution', file: 'MES_Extraction.xlsx', text: 'Operations performed, planned vs actual times, incidents.' },
  { id: 'PLM', name: 'Parts', file: 'PLM_DataSet.xlsx', text: 'Parts, cost, supplier, lead time and criticality.' },
  { id: 'ERP', name: 'Teams', file: 'ERP_Equipes_Airplus.xlsx', text: 'Operators, hourly cost, experience and rotations.' },
];

/** Landing page: data sources, standard reports and the cross analyses catalogue. */
export default function HomeView({ loading, actions }) {
  return (
    <div className="home">
      <section className="home-hero">
        <div className="eyebrow">Aircraft assembly line</div>
        <h2>Production analytics</h2>
        <p>
          Cross the execution data (MES), the parts catalogue (PLM) and the teams (ERP) to find where the line loses
          time and money, and what to fix first.
        </p>
      </section>

      <div className="source-grid">
        {SOURCES.map((s) => (
          <div key={s.id} className="source-card">
            <span className="source-tag">{s.id}</span>
            <div className="source-name">{s.name}</div>
            <p>{s.text}</p>
            <code>{s.file}</code>
          </div>
        ))}
      </div>

      <h3 className="home-section">Cross analyses</h3>
      <div className="analysis-grid">
        {ANALYSES.map((a) => {
          const Icon = a.icon;
          return (
            <button key={a.id} className="analysis-card" onClick={() => actions.analysis(a)} disabled={loading}>
              <span className="analysis-card-head">
                <span className="analysis-icon">
                  <Icon size={18} strokeWidth={1.8} />
                </span>
                {a.isNew && <span className="new-badge">New</span>}
                <ArrowUpRight size={16} className="analysis-arrow" />
              </span>
              <span className="analysis-card-title">{a.title}</span>
              <span className="analysis-card-desc">{a.description}</span>
              <span className="analysis-tags">
                {a.sources.map((source) => (
                  <span key={source} className="analysis-tag">
                    {source}
                  </span>
                ))}
              </span>
            </button>
          );
        })}
      </div>

      <h3 className="home-section">Standard reports</h3>
      <div className="report-grid">
        {REPORTS.map((r) => {
          const Icon = r.icon;
          return (
            <button key={r.id} className="report-chip" onClick={actions[r.action]} disabled={loading}>
              <Icon size={16} strokeWidth={1.8} />
              {r.title}
            </button>
          );
        })}
      </div>
    </div>
  );
}
