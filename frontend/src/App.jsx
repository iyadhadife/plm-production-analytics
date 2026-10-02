import { useState } from 'react';
import Chatbot from './components/chatbot/Chatbot.jsx';
import FileSidebar from './components/layout/FileSidebar.jsx';
import Header from './components/layout/Header.jsx';
import QuickAccessPanel from './components/layout/QuickAccessPanel.jsx';
import AnalysesModal from './components/modals/AnalysesModal.jsx';
import WorkflowModal from './components/modals/WorkflowModal.jsx';
import FullscreenReport from './components/preview/FullscreenReport.jsx';
import PreviewArea from './components/preview/PreviewArea.jsx';
import useDashboard from './hooks/useDashboard.js';
import useSteps from './hooks/useSteps.js';

export default function App() {
  const { status, files, selectedFile, selectFile, upload, report, reports } = useDashboard();
  const steps = useSteps();

  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isQuickAccessOpen, setIsQuickAccessOpen] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [modal, setModal] = useState(null); // 'workflow' | 'analyses' | null

  const closeModal = () => setModal(null);

  const headerActions = {
    teamExperience: reports.teamExperience,
    stepCosts: reports.stepCosts,
    delays: reports.delays,
    openWorkflow: () => setModal('workflow'),
    openAnalyses: () => setModal('analyses'),
    toggleQuickAccess: () => setIsQuickAccessOpen(!isQuickAccessOpen),
  };

  return (
    <div className="app-container">
      <Chatbot />

      {isFullscreen && report.html ? (
        <FullscreenReport html={report.html} onExit={() => setIsFullscreen(false)} />
      ) : (
        <>
          <FileSidebar isOpen={isSidebarOpen} files={files} selectedFile={selectedFile} onSelect={selectFile} />

          <div className="main-content">
            <Header
              title={selectedFile ? selectedFile.name : 'Dashboard'}
              status={status}
              loading={report.loading}
              actions={headerActions}
              isQuickAccessOpen={isQuickAccessOpen}
              onToggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
              onUpload={upload}
            />
            <PreviewArea
              selectedFile={selectedFile}
              reportHtml={report.html}
              onFullscreen={() => setIsFullscreen(true)}
              onCloseReport={report.clear}
            />
          </div>

          <QuickAccessPanel
            isOpen={isQuickAccessOpen}
            steps={steps}
            loading={report.loading}
            onClose={() => setIsQuickAccessOpen(false)}
            onShowStepDetails={reports.stepDetails}
          />
        </>
      )}

      {modal === 'analyses' && (
        <AnalysesModal
          loading={report.loading}
          onClose={closeModal}
          onSelect={(analysis) => {
            closeModal();
            reports.analysis(analysis);
          }}
        />
      )}
      {modal === 'workflow' && (
        <WorkflowModal
          steps={steps}
          loading={report.loading}
          onClose={closeModal}
          onSubmit={(step, maxNodes) => {
            closeModal();
            reports.workflow(step || null, maxNodes);
          }}
        />
      )}
    </div>
  );
}
