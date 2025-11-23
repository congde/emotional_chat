import { useState, useCallback } from 'react';
import { detectURLs } from '../utils/formatters';

export const useURLDetection = () => {
  const [detectedURLs, setDetectedURLs] = useState([]);

  // 防抖URL检测
  const debouncedDetectURLs = useCallback((text) => {
    const timeoutId = setTimeout(() => {
      const urls = detectURLs(text);
      setDetectedURLs(urls);
    }, 300);
    return () => clearTimeout(timeoutId);
  }, []);

  return {
    detectedURLs,
    setDetectedURLs,
    debouncedDetectURLs
  };
};

