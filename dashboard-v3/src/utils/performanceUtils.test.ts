import { describe, it, expect } from 'vitest';
import {
  formatSeconds,
  calculatePercentage,
  calculateResourcePercentage,
  calculateProcessingTime,
  calculateInteractionTime,
  formatDuration
} from './performanceUtils';

describe('performanceUtils', () => {
  describe('formatSeconds', () => {
    it('formats seconds with 2 decimal places', () => {
      expect(formatSeconds(1.2345)).toBe('1.23s');
      expect(formatSeconds(0)).toBe('0.00s');
      expect(formatSeconds(10)).toBe('10.00s');
    });
  });

  describe('calculatePercentage', () => {
    it('calculates percentage correctly', () => {
      expect(calculatePercentage(25, 100)).toBe(25);
      expect(calculatePercentage(50, 200)).toBe(25);
      expect(calculatePercentage(0, 100)).toBe(0);
    });

    it('handles zero total correctly', () => {
      expect(calculatePercentage(25, 0)).toBe(0);
    });
  });

  describe('calculateResourcePercentage', () => {
    it('calculates resource percentage correctly', () => {
      expect(calculateResourcePercentage(4000, 8000)).toBe(50);
      expect(calculateResourcePercentage(2000)).toBe(25); // Using default max value
    });

    it('caps percentage at 100', () => {
      expect(calculateResourcePercentage(10000, 8000)).toBe(100);
    });
  });

  describe('calculateProcessingTime', () => {
    it('calculates total processing time correctly', () => {
      const metrics = {
        stt: 0.5,
        llm: 2.0,
        tts: 0.8,
        tool_seconds: 0.3,
        memory_seconds: 0.1
      };
      expect(calculateProcessingTime(metrics)).toBeCloseTo(3.7, 1);
    });

    it('handles zero values correctly', () => {
      const metrics = {
        stt: 0,
        llm: 0,
        tts: 0,
        tool_seconds: 0,
        memory_seconds: 0
      };
      expect(calculateProcessingTime(metrics)).toBe(0);
    });
  });

  describe('calculateInteractionTime', () => {
    it('calculates total interaction time correctly', () => {
      const metrics = {
        stt: 0.5,
        llm: 2.0,
        tts: 0.8,
        tool_seconds: 0.3,
        memory_seconds: 0.1,
        stt_audio: 1.5,
        tts_audio: 2.0
      };
      expect(calculateInteractionTime(metrics)).toBeCloseTo(7.2, 1);
    });
  });

  describe('formatDuration', () => {
    it('formats duration with hours, minutes, and seconds', () => {
      expect(formatDuration(3661000)).toBe('1h 1m 1s');
    });

    it('formats duration with minutes and seconds', () => {
      expect(formatDuration(65000)).toBe('1m 5s');
    });

    it('formats duration with only seconds', () => {
      expect(formatDuration(5000)).toBe('5s');
    });

    it('handles zero duration', () => {
      expect(formatDuration(0)).toBe('0s');
    });

    it('handles negative duration', () => {
      expect(formatDuration(-1000)).toBe('0s');
    });
  });
});
