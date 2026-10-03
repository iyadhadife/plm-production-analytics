import { useState } from 'react';
import Chatbot from './components/chatbot/Chatbot.jsx';
import Header from './components/layout/Header.jsx';
import NavSidebar from './components/layout/NavSidebar.jsx';
import QuickAccessPanel from './components/layout/QuickAccessPanel.jsx';
import WorkflowModal from './components/modals/WorkflowModal.jsx';
import FullscreenReport from './components/preview/FullscreenReport.jsx';
import PreviewArea from './components/preview/PreviewArea.jsx';
import useDashboard from './hooks/useDashboard.js';
import useSteps from './hooks/useSteps.js';

export default function App() {
  const { status, files, selectedFile, selectFile, upload, report, reports, view, goHome } = useDashboard();
  const steps = useSteps();

  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isQuickAccessOpen, setIsQuickAccessOpen] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isWorkflowOpen, setIsWorkflowOpen] = useState(false);

  const actions = {
    ...reports,
    goHome,
    openWorkflow: () => setIsWorkflowOpen(true),
    toggleQuickAccess: () => setIsQuickAccessOpen(!isQuickAccessOpen),
  };

  return (
    <div className="app-container">
      <Chatbot />

      {isFullscreen && report.html ? (
        <FullscreenReport html={report.html} onExit={() => setIsFullscreen(false)} />
      ) : (
        <>
          <NavSidebar
            isOpen={isSidebarOpen}
            view={view}
            loading={report.loading}
            files={files}
            selectedFile={selectedFile}
            actions={actions}
            onSelectFile={selectFile}
          />

          <div className="main-content">
            <Header
              view={view}
              status={status}
              hasReport={Boolean(report.html)}
              onToggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
              onUpload={upload}
              onFullscreen={() => setIsFullscreen(true)}
              onClose={goHome}
            />
            <PreviewArea
              selectedFile={selectedFile}
              reportHtml={report.html}
              loading={report.loading}
              actions={actions}
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

      {isWorkflowOpen && (
        <WorkflowModal
          steps={steps}
          loading={report.loading}
          onClose={() => setIsWorkflowOpen(false)}
          onSubmit={(step, maxNodes) => {
            setIsWorkflowOpen(false);
            reports.workflow(step || null, maxNodes);
          }}
        />
      )}
    </div>
  );
}
