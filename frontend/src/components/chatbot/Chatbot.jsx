import { useEffect, useRef, useState } from 'react';
import { MessageCircle } from 'lucide-react';
import ChatHeader from './ChatHeader.jsx';
import ChatInput from './ChatInput.jsx';
import ChatMessage from './ChatMessage.jsx';
import TypingIndicator from './TypingIndicator.jsx';
import useChat from './useChat.js';
import '../../styles/chatbot.css';
import '../../styles/chatbot-messages.css';

/** Floating chat widget that queries the Excel files through Gemini + pandas. */
export default function Chatbot() {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const { messages, isLoading, ask } = useChat();
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  if (!isOpen) {
    return (
      <button onClick={() => setIsOpen(true)} className="chatbot-fab" title="Open the chatbot">
        <MessageCircle size={24} />
      </button>
    );
  }

  return (
    <div className={`chatbot-container ${isMinimized ? 'minimized' : ''}`}>
      <ChatHeader
        isMinimized={isMinimized}
        onToggleMinimize={() => setIsMinimized(!isMinimized)}
        onClose={() => setIsOpen(false)}
      />
      {!isMinimized && (
        <>
          <div className="chatbot-messages">
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            {isLoading && <TypingIndicator />}
            <div ref={endRef} />
          </div>
          <ChatInput disabled={isLoading} onSend={ask} />
        </>
      )}
    </div>
  );
}
