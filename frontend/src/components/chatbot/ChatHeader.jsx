import { MessageCircle, Minimize2, X } from 'lucide-react';

export default function ChatHeader({ isMinimized, onToggleMinimize, onClose }) {
  return (
    <div className="chatbot-header">
      <div className="chatbot-header-title">
        <MessageCircle size={20} />
        <span>Excel assistant</span>
      </div>
      <div className="chatbot-header-actions">
        <button onClick={onToggleMinimize} className="chatbot-icon-btn" title={isMinimized ? 'Expand' : 'Minimise'}>
          <Minimize2 size={16} />
        </button>
        <button onClick={onClose} className="chatbot-icon-btn" title="Close">
          <X size={16} />
        </button>
      </div>
    </div>
  );
}
