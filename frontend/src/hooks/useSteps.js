import { useEffect, useState } from 'react';
import { fetchSteps } from '../api/reports.js';

/** Assembly step names read from the MES file. */
export default function useSteps() {
  const [steps, setSteps] = useState([]);

  useEffect(() => {
    fetchSteps().then(setSteps).catch(() => setSteps([]));
  }, []);

  return steps;
}
