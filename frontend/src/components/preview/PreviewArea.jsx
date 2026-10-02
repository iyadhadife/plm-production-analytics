import EmptyState from './EmptyState.jsx';
import FilePreview from './FilePreview.jsx';
import ReportFrame from './ReportFrame.jsx';
import ResultBanner from './ResultBanner.jsx';

/** Central area: the current report, else the selected file, else an empty state. */
export default function PreviewArea({ selectedFile, reportHtml, onFullscreen, onCloseReport }) {
  if (!selectedFile && !reportHtml) {
    return (
      <main className="preview-area">
        <EmptyState />
      </main>
    );
  }

  return (
    <main className="preview-area">
      <div className="preview-card">
        {reportHtml && <ResultBanner onFullscreen={onFullscreen} onClose={onCloseReport} />}

        <div className="preview-card-header">
          {selectedFile ? (
            <>
              <span>ID: {selectedFile.id}</span>
              <span className="file-type-badge">{selectedFile.type}</span>
            </>
          ) : null}
        </div>

        <div className="preview-card-body">
          {reportHtml ? (
            <div className="report-frame-wrap">
              <ReportFrame html={reportHtml} />
            </div>
          ) : (
            <FilePreview file={selectedFile} />
          )}
        </div>
      </div>
    </main>
  );
}
