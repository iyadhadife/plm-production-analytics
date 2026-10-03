import { Download, FileSpreadsheet, FileText, Image as ImageIcon } from 'lucide-react';
import { getFileUrl } from '../../api/client.js';

function FileIcon({ file }) {
  if (file.type.includes('image')) return <ImageIcon size={16} strokeWidth={1.8} />;
  if (/\.(xlsx?|csv)$/i.test(file.name)) return <FileSpreadsheet size={16} strokeWidth={1.8} />;
  return <FileText size={16} strokeWidth={1.8} />;
}

export default function FileListItem({ file, selected, onSelect }) {
  return (
    <div className={`file-item ${selected ? 'selected' : ''}`}>
      <button className="file-item-main" onClick={() => onSelect(file)} title={file.name}>
        <FileIcon file={file} />
        <span className="file-info">
          <span className="file-name">{file.name}</span>
          <span className="file-size">{file.size}</span>
        </span>
      </button>
      <a href={getFileUrl(file.url)} download={file.name} className="download-btn" title="Download file">
        <Download size={14} />
      </a>
    </div>
  );
}
