import { useCallback, useState } from 'react';

const EMPTY = { type: '', message: '' };

/** Status badge state: { type: 'loading' | 'success' | 'error' | '', message }. */
export default function useStatus() {
  const [status, setStatus] = useState(EMPTY);

  const showError = useCallback((message) => setStatus({ type: 'error', message }), []);
  const showSuccess = useCallback((message) => setStatus({ type: 'success', message }), []);
  const showLoading = useCallback((message) => setStatus({ type: 'loading', message }), []);
  const clear = useCallback(() => setStatus(EMPTY), []);

  return { status, showError, showSuccess, showLoading, clear };
}
