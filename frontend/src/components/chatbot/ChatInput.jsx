import { useEffect, useRef, useState } from 'react';
import { Send } from 'lucide-react';

export default function ChatInput({ disabled, onSend }) {
  const [value, setValue] = useState('');
  const inputRef = useRef(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const send = () => {
    const question = value.trim();
    if (!question || disabled) return;
    onSend(question);
    setValue('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  return (
    <div className="chatbot-input-area">
      <input
        ref={inputRef}
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask a question about the Excel files..."
        className="chatbot-input"
        disabled={disabled}
      />
      <button onClick={send} className="chatbot-send-btn" disabled={!value.trim() || disabled} title="Send">
        <Send size={18} />
      </button>
    </div>
  );
}
