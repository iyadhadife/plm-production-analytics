import { getJson, getText } from './client.js';

export const fetchSteps = () => getJson('/api/steps');

export const fetchStepDetails = (step) =>
  getText(`/api/reports/step-details?${new URLSearchParams({ step })}`);

export const fetchStepCosts = () => getText('/api/reports/step-costs');

export const fetchTeamExperience = () => getText('/api/reports/team-experience');

export const fetchDelays = () => getText('/api/reports/delays');

export const fetchWorkflow = (step, maxNodes) => {
  const params = new URLSearchParams({ max_nodes: maxNodes });
  if (step) params.set('step', step);
  return getText(`/api/reports/workflow?${params}`);
};

export const fetchAnalysis = (id) => getText(`/api/analyses/${id}`);
