import { useCallback, useState } from 'react';
import { fetchExcelTable, uploadFile } from '../api/files.js';
import {
  fetchAnalysis, fetchDelays, fetchStepCosts, fetchStepDetails, fetchTeamExperience, fetchWorkflow,
} from '../api/reports.js';
import useFiles from './useFiles.js';
import useReport from './useReport.js';
import useStatus from './useStatus.js';

const STATUS_CLEAR_DELAY_MS = 3000;

/**
 * State and actions of the dashboard: files, selected file, current report, status.
 * `view` describes what is displayed: { id, title, subtitle } or null for the home page.
 */
export default function useDashboard() {
  const { status, showError, showSuccess, showLoading, clear: clearStatus } = useStatus();
  const { files, reload: reloadFiles } = useFiles(showError);
  const report = useReport({ onSuccess: showSuccess, onError: showError });
  const [selectedFile, setSelectedFile] = useState(null);
  const [view, setView] = useState(null);

  // Reports built from the three source files replace the selected file.
  const showReport = useCallback(
    async (fetcher, nextView) => {
      setSelectedFile(null);
      if (await report.load(fetcher, `${nextView.title} loaded`)) setView(nextView);
    },
    [report],
  );

  const selectFile = (file) => {
    setSelectedFile(file);
    setView({ id: `file:${file.id}`, title: file.name, subtitle: 'Document' });
    report.clear();
    if (file.name.endsWith('.xlsx')) {
      report.load(() => fetchExcelTable(file.name), `Table ${file.name} loaded`);
    }
  };

  const goHome = () => {
    setSelectedFile(null);
    setView(null);
    report.clear();
  };

  const upload = async (file) => {
    showLoading('Uploading...');
    try {
      await uploadFile(file);
      showSuccess('File uploaded');
      await reloadFiles();
      setTimeout(clearStatus, STATUS_CLEAR_DELAY_MS);
    } catch (error) {
      showError(error.message);
    }
  };

  const reportView = (id, title) => ({ id, title, subtitle: 'Report' });
  const reports = {
    teamExperience: () =>
      showReport(fetchTeamExperience, reportView('team-experience', 'Team experience by week')),
    stepCosts: () => showReport(fetchStepCosts, reportView('step-costs', 'Costs by step')),
    delays: () => showReport(fetchDelays, reportView('delays', 'Delays > 10 min')),
    workflow: (step, maxNodes) =>
      showReport(() => fetchWorkflow(step, maxNodes), reportView('workflow', 'Sankey workflow')),
    stepDetails: (step) =>
      showReport(() => fetchStepDetails(step), { id: 'step-details', title: step, subtitle: 'Step details' }),
    analysis: (analysis) =>
      showReport(() => fetchAnalysis(analysis.id), {
        id: `analysis:${analysis.id}`,
        title: analysis.title,
        subtitle: `Cross analysis · ${analysis.sources.join(' × ')}`,
      }),
  };

  return { status, files, selectedFile, selectFile, upload, report, reports, view, goHome };
}
