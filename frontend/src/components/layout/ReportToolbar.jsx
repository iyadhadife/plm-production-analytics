/** Buttons that open the dashboard reports. */
export default function ReportToolbar({ loading, actions, isQuickAccessOpen }) {
  const label = (text) => (loading ? 'Loading...' : text);

  return (
    <>
      <div className="buttons-container">
        <button onClick={actions.teamExperience} className="primary-btn green" disabled={loading}>
          {label('Team experience by week')}
        </button>
        <button onClick={actions.stepCosts} className="primary-btn orange" disabled={loading}>
          {label('Costs by step')}
        </button>
        <button onClick={actions.openWorkflow} className="primary-btn purple" disabled={loading}>
          {label('Sankey workflow')}
        </button>
        <button onClick={actions.openAnalyses} className="primary-btn blue" disabled={loading}>
          {label('🔗 Cross analyses')}
        </button>
      </div>

      <button onClick={actions.delays} className="primary-btn red" disabled={loading}>
        {label('⚠️ Delays > 10 min')}
      </button>

      <button onClick={actions.toggleQuickAccess} className="primary-btn grey">
        {isQuickAccessOpen ? '✕ Close' : '☰ Quick access'}
      </button>
    </>
  );
}
