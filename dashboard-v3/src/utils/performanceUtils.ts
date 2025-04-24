/**
 * Format seconds to a readable string with 2 decimal places
 * @param seconds Number of seconds
 * @returns Formatted string with 's' suffix
 */
export const formatSeconds = (seconds: number): string => {
  return seconds.toFixed(2) + 's';
};

/**
 * Calculate the percentage of a value relative to a total
 * @param value The value to calculate percentage for
 * @param total The total value (100%)
 * @returns Percentage as a number between 0-100
 */
export const calculatePercentage = (value: number, total: number): number => {
  if (!total) return 0;
  return (value / total) * 100;
};

/**
 * Calculate the percentage of system resource usage
 * @param value Current usage value
 * @param maxValue Maximum expected value (default: 8000 for 8GB)
 * @returns Percentage as a number between 0-100, capped at 100
 */
export const calculateResourcePercentage = (value: number, maxValue: number = 8000): number => {
  return Math.min((value / maxValue) * 100, 100);
};

/**
 * Calculate the total processing time excluding audio durations
 * @param metrics Performance metrics object
 * @returns Total processing time in seconds
 */
export const calculateProcessingTime = (metrics: {
  stt: number;
  llm: number;
  tts: number;
  tool_seconds: number;
  memory_seconds: number;
}): number => {
  return metrics.stt + metrics.llm + metrics.tts + metrics.tool_seconds + metrics.memory_seconds;
};

/**
 * Calculate the total interaction time including audio durations
 * @param metrics Performance metrics object
 * @returns Total interaction time in seconds
 */
export const calculateInteractionTime = (metrics: {
  stt: number;
  llm: number;
  tts: number;
  tool_seconds: number;
  memory_seconds: number;
  stt_audio: number;
  tts_audio: number;
}): number => {
  return calculateProcessingTime(metrics) + metrics.stt_audio + metrics.tts_audio;
};

/**
 * Format a timestamp in milliseconds to a readable duration string
 * @param ms Timestamp in milliseconds
 * @returns Formatted duration string (e.g., "2h 30m 15s" or "45m 20s" or "10s")
 */
export const formatDuration = (ms: number): string => {
  if (ms <= 0) return '0s';
  
  const seconds = Math.floor((ms / 1000) % 60);
  const minutes = Math.floor((ms / (1000 * 60)) % 60);
  const hours = Math.floor(ms / (1000 * 60 * 60));
  
  let result = '';
  if (hours > 0) {
    result += `${hours}h `;
  }
  if (minutes > 0 || hours > 0) {
    result += `${minutes}m `;
  }
  result += `${seconds}s`;
  
  return result;
};
