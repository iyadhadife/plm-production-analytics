import { Download, FileText, Image as ImageIcon } from 'lucide-react';
import { getFileUrl } from '../../api/client.js';

export default function FileListItem({ file, selected, onSelect }) {
  return (
    <div className={`file-item ${selected ? 'selected' : ''}`}>
      <div className="file-item-main" onClick={() => onSelect(file)}>
        <div className="file-icon-wrapper">
          {file.type.includes('image') ? <ImageIcon size={18} /> : <FileText size={18} />}
        </div>
        <div className="file-info">
          <p className="file-name">{file.name}</p>
          <p className="file-size">{file.size}</p>
        </div>
      </div>
      <a href={getFileUrl(file.url)} download={file.name} className="download-btn" title="Download file">
        <Download size={14} />
      </a>
    </div>
  );
}
