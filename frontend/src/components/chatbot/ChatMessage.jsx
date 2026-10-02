import formatMessage from './formatMessage.jsx';

export default function ChatMessage({ message }) {
  return (
    <div className={`chatbot-message ${message.type}`}>
      <div className={`message-bubble ${message.error ? 'error' : ''}`}>
        {message.text.includes('<table') ? (
          <div dangerouslySetInnerHTML={{ __html: message.text }} />
        ) : (
          <div className="message-text">{formatMessage(message.text)}</div>
        )}

        {message.code && (
          <details className="message-code-details">
            <summary>Generated pandas code</summary>
            <pre className="message-code">{message.code}</pre>
          </details>
        )}
      </div>
      <div className="message-time">
        {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
      </div>
    </div>
  );
}
