/** Sandboxed iframe rendering an HTML report returned by the backend. */
export default function ReportFrame({ html, title = 'Report' }) {
  return (
    <iframe
      title={title}
      srcDoc={html}
      className="report-frame"
      sandbox="allow-scripts allow-same-origin allow-popups"
    />
  );
}
