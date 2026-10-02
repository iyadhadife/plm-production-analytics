// Backend base URL; override with VITE_API_URL in frontend/.env.local.
export const BACKEND_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

/** Turns a backend path (e.g. /uploads/file.png) into an absolute URL. */
export const getFileUrl = (path) => {
  if (!path) return '';
  if (path.startsWith('http')) return path;
  return `${BACKEND_URL}${path}`;
};

const errorMessage = async (response) => {
  try {
    const data = await response.json();
    // routes answer { error: "message" }, the chat route { answer: "message", error: true }
    if (typeof data?.error === 'string') return data.error;
    if (data?.answer) return data.answer;
  } catch {
    // body is not JSON
  }
  return `Error ${response.status}`;
};

/** fetch() wrapper: throws an Error carrying the backend message on non-2xx responses. */
export const request = async (path, options = {}) => {
  let response;
  try {
    response = await fetch(`${BACKEND_URL}${path}`, options);
  } catch {
    throw new Error('Backend unreachable — is it running on port 5000?');
  }
  if (!response.ok) throw new Error(await errorMessage(response));
  return response;
};

export const getJson = async (path, options) => (await request(path, options)).json();
export const getText = async (path) => (await request(path)).text();
