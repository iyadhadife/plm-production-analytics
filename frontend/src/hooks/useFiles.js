import { useCallback, useEffect, useState } from 'react';
import { fetchFiles } from '../api/files.js';

/** Uploaded files list, loaded on mount; `reload` refreshes it. */
export default function useFiles(onError) {
  const [files, setFiles] = useState([]);

  const reload = useCallback(
    () =>
      fetchFiles()
        .then(setFiles)
        .catch((error) => onError(error.message || 'Could not load the files.')),
    [onError],
  );

  useEffect(() => {
    fetchFiles()
      .then(setFiles)
      .catch((error) => onError(error.message || 'Could not load the files.'));
  }, [onError]);

  return { files, reload };
}
