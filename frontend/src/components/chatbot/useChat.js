import { useState } from 'react';
import { sendChatMessage } from '../../api/chat.js';

const WELCOME = {
  id: 1,
  type: 'bot',
  text: "👋 Hello! I can answer questions about the Excel files. For example: 'Which assemblies take the longest?'",
  timestamp: new Date(),
};

/** Conversation state and the call to the chatbot API. */
export default function useChat() {
  const [messages, setMessages] = useState([WELCOME]);
  const [isLoading, setIsLoading] = useState(false);

  const add = (message) => setMessages((prev) => [...prev, { id: Date.now() + Math.random(), timestamp: new Date(), ...message }]);

  const ask = async (question) => {
    add({ type: 'user', text: question });
    setIsLoading(true);
    try {
      const response = await sendChatMessage(question);
      add({ type: 'bot', text: response.answer, code: response.code, error: response.error });
    } catch (error) {
      add({ type: 'bot', text: `❌ Error: ${error.message}`, error: true });
    } finally {
      setIsLoading(false);
    }
  };

  return { messages, isLoading, ask };
}
