/** Overlay + dialog; clicking outside the dialog closes it. */
export default function Modal({ title, className = '', onClose, children }) {
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className={`modal-content ${className}`} onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">{title}</div>
        {children}
      </div>
    </div>
  );
}
