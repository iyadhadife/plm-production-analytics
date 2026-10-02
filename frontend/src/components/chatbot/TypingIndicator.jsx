export default function TypingIndicator() {
  return (
    <div className="chatbot-message bot">
      <div className="message-bubble loading">
        <div className="typing-indicator">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    </div>
  );
}
