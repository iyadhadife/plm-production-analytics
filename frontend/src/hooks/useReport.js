import { useCallback, useState } from 'react';

/**
 * HTML report currently displayed in the preview iframe.
 * `load(fetcher, successMessage)` runs a fetcher that resolves to HTML.
 */
export default function useReport({ onSuccess, onError }) {
  const [html, setHtml] = useState('');
  const [loading, setLoading] = useState(false);

  const load = useCallback(
    async (fetcher, successMessage) => {
      setLoading(true);
      try {
        setHtml(await fetcher());
        onSuccess(successMessage);
        return true;
      } catch (error) {
        onError(error.message);
        return false;
      } finally {
        setLoading(false);
      }
    },
    [onSuccess, onError],
  );

  const clear = useCallback(() => setHtml(''), []);

  return { html, loading, load, clear };
}
