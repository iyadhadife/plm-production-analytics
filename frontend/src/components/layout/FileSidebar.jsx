import FileListItem from './FileListItem.jsx';

export default function FileSidebar({ isOpen, files, selectedFile, onSelect }) {
  return (
    <div className={`sidebar ${isOpen ? 'open' : 'closed'}`}>
      <div className="sidebar-header">
        <span className="sidebar-title">My documents</span>
        <span className="file-count">{files.length}</span>
      </div>

      <div className="file-list">
        {files.length === 0 ? (
          <div className="empty-state-text">No files</div>
        ) : (
          files.map((file) => (
            <FileListItem key={file.id} file={file} selected={selectedFile?.id === file.id} onSelect={onSelect} />
          ))
        )}
      </div>
    </div>
  );
}
