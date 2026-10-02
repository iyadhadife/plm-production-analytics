import { FileText } from 'lucide-react';
import { getFileUrl } from '../../api/client.js';

/** Image preview, or a link to open files that cannot be previewed. */
export default function FilePreview({ file }) {
  const url = getFileUrl(file.url);
  return (
    <div className="file-preview">
      {file.type.includes('image') ? (
        <img src={url} alt="Preview" className="preview-image" />
      ) : (
        <div className="no-preview-box">
          <div className="icon-circle">
            <FileText size={40} />
          </div>
          <h3>{file.name}</h3>
          <p>No preview available.</p>
          <a href={url} target="_blank" rel="noopener noreferrer" className="link-btn">
            Open file
          </a>
        </div>
      )}
    </div>
  );
}
