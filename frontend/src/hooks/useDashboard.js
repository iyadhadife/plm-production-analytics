import { useCallback, useState } from 'react';
import { fetchExcelTable, uploadFile } from '../api/files.js';
import {
  fetchAnalysis, fetchDelays, fetchStepCosts, fetchStepDetails, fetchTeamExperience, fetchWorkflow,
} from '../api/reports.js';
import useFiles from './useFiles.js';
import useReport from './useReport.js';
import useStatus from './useStatus.js';

const STATUS_CLEAR_DELAY_MS = 3000;

/** State and actions of the dashboard: files, selected file, current report, status. */
export default function useDashboard() {
  const { status, showError, showSuccess, showLoading, clear: clearStatus } = useStatus();
  const { files, reload: reloadFiles } = useFiles(showError);
  const report = useReport({ onSuccess: showSuccess, onError: showError });
  const [selectedFile, setSelectedFile] = useState(null);

  // Reports built from the three source files replace the selected file.
  const showReport = useCallback(
    (fetcher, message) => {
      setSelectedFile(null);
      return report.load(fetcher, message);
    },
    [report],
  );

  const selectFile = (file) => {
    setSelectedFile(file);
    report.clear();
    if (file.name.endsWith('.xlsx')) {
      report.load(() => fetchExcelTable(file.name), `Table ${file.name} loaded`);
    }
  };

  const upload = async (file) => {
    showLoading('Uploading...');
    try {
      await uploadFile(file);
      showSuccess('File uploaded!');
      await reloadFiles();
      setTimeout(clearStatus, STATUS_CLEAR_DELAY_MS);
    } catch (error) {
      showError(error.message);
    }
  };

  const reports = {
    teamExperience: () => showReport(fetchTeamExperience, 'Team experience loaded'),
    stepCosts: () => showReport(fetchStepCosts, 'Costs by step loaded'),
    delays: () => showReport(fetchDelays, 'Delays > 10 min loaded'),
    workflow: (step, maxNodes) => showReport(() => fetchWorkflow(step, maxNodes), 'Sankey workflow loaded'),
    stepDetails: (step) => showReport(() => fetchStepDetails(step), 'Step details loaded'),
    analysis: (analysis) => showReport(() => fetchAnalysis(analysis.id), `${analysis.title} loaded`),
  };

  return { status, files, selectedFile, selectFile, upload, report, reports };
}
