import {
  AlertTriangle, CalendarRange, Clock, Coins, Gauge, HardHat, PiggyBank, Target, Truck, Users, Workflow,
} from 'lucide-react';

// Cross analyses served by /api/analyses/<id> (backend/app/analytics).
export const ANALYSES = [
  {
    id: 'overview',
    title: '360° overview',
    icon: Gauge,
    description: 'Key KPIs, planned vs actual S-curve, delay by step and operations with the highest financial exposure.',
    sources: ['MES', 'PLM', 'ERP'],
  },
  {
    id: 'priority-matrix',
    title: 'Risk × value matrix',
    icon: Target,
    description: 'Which stations to address first: overrun vs value and criticality of the committed parts.',
    sources: ['MES', 'PLM', 'ERP'],
  },
  {
    id: 'pareto',
    title: 'Incident Pareto',
    icon: AlertTriangle,
    description: 'The incident families that cause 80 % of the delay, where they happen and their root causes.',
    sources: ['MES', 'PLM', 'ERP'],
  },
  {
    id: 'schedule',
    title: 'Schedule reliability',
    icon: Clock,
    description: 'Are the standard times realistic? Planned vs actual, overrun by hour, end-of-day drift, new standards.',
    sources: ['MES'],
    isNew: true,
  },
  {
    id: 'cost-structure',
    title: 'Cost structure',
    icon: PiggyBank,
    description: 'Parts vs labour per step, supplier → part treemap, cost density (€/kg) and the parts that weigh most.',
    sources: ['MES', 'PLM', 'ERP'],
    isNew: true,
  },
  {
    id: 'supply-risk',
    title: 'Supply risk',
    icon: Truck,
    description: 'Critical long-lead parts, supplier dependency and the top 10 parts to secure.',
    sources: ['PLM', 'MES'],
  },
  {
    id: 'experience',
    title: 'Experience vs performance',
    icon: HardHat,
    description: 'Does team experience affect overruns? Hourly cost by level.',
    sources: ['MES', 'ERP'],
  },
  {
    id: 'workforce',
    title: 'Workforce & succession',
    icon: Users,
    description: 'Age pyramid, experts close to retirement, certifications coverage and weekly rotations.',
    sources: ['ERP', 'MES'],
    isNew: true,
  },
  {
    id: 'timeline',
    title: 'Timeline (Gantt)',
    icon: CalendarRange,
    description: 'Every operation, planned vs actual, over time, coloured by parts criticality.',
    sources: ['MES', 'PLM', 'ERP'],
  },
];

// Standard reports served by /api/reports/<id>; `action` is the key in useDashboard().reports.
export const REPORTS = [
  { id: 'team-experience', action: 'teamExperience', title: 'Team experience by week', icon: Users },
  { id: 'step-costs', action: 'stepCosts', title: 'Costs by step', icon: Coins },
  { id: 'workflow', action: 'openWorkflow', title: 'Sankey workflow', icon: Workflow },
  { id: 'delays', action: 'delays', title: 'Delays > 10 min', icon: AlertTriangle },
];
