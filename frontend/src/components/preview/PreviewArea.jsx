import FilePreview from './FilePreview.jsx';
import HomeView from './HomeView.jsx';
import ReportFrame from './ReportFrame.jsx';

/** Central area: the current report, else the selected file, else the home page. */
export default function PreviewArea({ selectedFile, reportHtml, loading, actions }) {
  if (!selectedFile && !reportHtml) {
    return (
      <main className="preview-area scroll">
        <HomeView loading={loading} actions={actions} />
        {loading && <div className="loading-bar" />}
      </main>
    );
  }

  return (
    <main className="preview-area">
      {loading && <div className="loading-bar" />}
      <div className="report-surface">
        {reportHtml ? <ReportFrame html={reportHtml} /> : <FilePreview file={selectedFile} />}
      </div>
    </main>
  );
}
