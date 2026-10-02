// Cross analyses served by /api/analyses/<id> (backend/app/analytics).
export const ANALYSES = [
  {
    id: 'overview',
    title: '📈 360° overview',
    description: 'Key KPIs, planned vs actual S-curve, delay by step and operations with the highest financial exposure.',
    sources: ['MES', 'PLM', 'ERP'],
  },
  {
    id: 'priority-matrix',
    title: '🎯 Risk × value matrix',
    description: 'Which stations to address first: overrun vs value and criticality of the committed parts.',
    sources: ['MES', 'PLM', 'ERP'],
  },
  {
    id: 'pareto',
    title: '⚠️ Incident Pareto',
    description: 'The incident families that cause 80 % of the delay, where they happen and their root causes.',
    sources: ['MES', 'PLM', 'ERP'],
  },
  {
    id: 'experience',
    title: '👷 Experience vs performance',
    description: 'Does team experience affect overruns? Hourly cost by level.',
    sources: ['MES', 'ERP'],
  },
  {
    id: 'supply-risk',
    title: '🚚 Supply risk',
    description: 'Critical long-lead parts, supplier dependency and the top 10 parts to secure.',
    sources: ['PLM', 'MES'],
  },
  {
    id: 'timeline',
    title: '🗓️ Timeline (Gantt)',
    description: 'Every operation, planned vs actual, over time, coloured by parts criticality.',
    sources: ['MES', 'PLM', 'ERP'],
  },
];
