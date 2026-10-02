import { getJson } from './client.js';

/** Sends a question to the chatbot; resolves to { answer, code, error }. */
export const sendChatMessage = (question) =>
  getJson('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  });
