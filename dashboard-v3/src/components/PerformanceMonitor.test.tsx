import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import PerformanceMonitor from './PerformanceMonitor';

// Mock the recharts library
vi.mock('recharts', () => {
  const OriginalModule = vi.importActual('recharts');
  return {
    ...OriginalModule,
    ResponsiveContainer: ({ children }: { children: React.ReactNode }) => <div data-testid="responsive-container">{children}</div>,
    PieChart: ({ children }: { children: React.ReactNode }) => <div data-testid="pie-chart">{children}</div>,
    Pie: ({ children }: { children: React.ReactNode }) => <div data-testid="pie">{children}</div>,
    BarChart: ({ children }: { children: React.ReactNode }) => <div data-testid="bar-chart">{children}</div>,
    LineChart: ({ children }: { children: React.ReactNode }) => <div data-testid="line-chart">{children}</div>,
    Bar: () => <div data-testid="bar"></div>,
    Line: () => <div data-testid="line"></div>,
    Cell: () => <div data-testid="cell"></div>,
    XAxis: () => <div data-testid="x-axis"></div>,
    YAxis: () => <div data-testid="y-axis"></div>,
    CartesianGrid: () => <div data-testid="cartesian-grid"></div>,
    Tooltip: () => <div data-testid="tooltip"></div>,
    Legend: () => <div data-testid="legend"></div>,
  };
});

describe('PerformanceMonitor', () => {
  const mockPerformanceMetrics = {
    stt: 0.5,
    llm: 2.3,
    tts: 0.8,
    total: 4.0,
    stt_audio: 1.5,
    tts_audio: 2.0,
    tool_seconds: 0.3,
    memory_seconds: 0.1
  };

  const mockSystemMetrics = {
    memory_mb: 1500,
    cpu_percent: 45.5,
    gpu_vram_mb: 2000
  };

  it('renders the component with title', () => {
    render(
      <PerformanceMonitor
        performanceMetrics={mockPerformanceMetrics}
        systemMetrics={mockSystemMetrics}
      />
    );

    expect(screen.getByText('Performance Metrics')).toBeInTheDocument();
  });

  it('displays processing time section with correct values in basic mode', () => {
    render(
      <PerformanceMonitor
        performanceMetrics={mockPerformanceMetrics}
        systemMetrics={mockSystemMetrics}
      />
    );

    // Basic mode should be active by default
    expect(screen.getByText('Basic')).toHaveClass('bg-primary-600');

    expect(screen.getByText('Processing Time')).toBeInTheDocument();
    expect(screen.getByText('Speech-to-Text')).toBeInTheDocument();
    expect(screen.getByText('0.50s')).toBeInTheDocument(); // STT time
    expect(screen.getByText('Language Model')).toBeInTheDocument();
    expect(screen.getByText('2.30s')).toBeInTheDocument(); // LLM time
    expect(screen.getByText('Text-to-Speech')).toBeInTheDocument();
    expect(screen.getByText('0.80s')).toBeInTheDocument(); // TTS time
    expect(screen.getByText('Tools')).toBeInTheDocument();
    expect(screen.getByText('0.30s')).toBeInTheDocument(); // Tools time
    expect(screen.getByText('Memory')).toBeInTheDocument();
    expect(screen.getByText('0.10s')).toBeInTheDocument(); // Memory time
    expect(screen.getByText('Total Processing')).toBeInTheDocument();
    expect(screen.getByText('4.00s')).toBeInTheDocument(); // Total time
  });

  it('displays system resources section with correct values in basic mode', () => {
    render(
      <PerformanceMonitor
        performanceMetrics={mockPerformanceMetrics}
        systemMetrics={mockSystemMetrics}
      />
    );

    expect(screen.getByText('System Resources')).toBeInTheDocument();
    expect(screen.getByText('CPU Usage')).toBeInTheDocument();
    expect(screen.getByText('45.5%')).toBeInTheDocument(); // CPU percentage
    expect(screen.getByText('Memory Usage')).toBeInTheDocument();
    expect(screen.getByText('1500 MB')).toBeInTheDocument(); // Memory usage
    expect(screen.getByText('GPU VRAM')).toBeInTheDocument();
    expect(screen.getByText('2000 MB')).toBeInTheDocument(); // GPU VRAM
    expect(screen.getByText('Audio Duration')).toBeInTheDocument();
    expect(screen.getByText(/Input: 1.50s \| Output: 2.00s/)).toBeInTheDocument(); // Audio durations
  });

  it('handles zero values correctly', () => {
    const zeroMetrics = {
      stt: 0,
      llm: 0,
      tts: 0,
      total: 0,
      stt_audio: 0,
      tts_audio: 0,
      tool_seconds: 0,
      memory_seconds: 0
    };

    render(
      <PerformanceMonitor
        performanceMetrics={zeroMetrics}
        systemMetrics={mockSystemMetrics}
      />
    );

    // Check for total processing time specifically
    expect(screen.getByText('Total Processing').nextSibling?.textContent).toBe('0.00s');
    // Check that we don't have NaN or undefined values
    expect(screen.queryByText(/NaN/)).not.toBeInTheDocument();
    expect(screen.queryByText(/undefined/)).not.toBeInTheDocument();
  });

  it('switches to detailed mode when the Detailed button is clicked', () => {
    render(
      <PerformanceMonitor
        performanceMetrics={mockPerformanceMetrics}
        systemMetrics={mockSystemMetrics}
      />
    );

    // Click the Detailed button
    fireEvent.click(screen.getByText('Detailed'));

    // Detailed mode should now be active
    expect(screen.getByText('Detailed')).toHaveClass('bg-primary-600');

    // Check for detailed mode elements
    expect(screen.getByText('Processing Time Breakdown')).toBeInTheDocument();
    expect(screen.getByText('Historical Performance')).toBeInTheDocument();

    // Check for chart containers
    expect(screen.getAllByTestId('responsive-container').length).toBeGreaterThan(0);
  });

  it('displays the correct metrics in detailed mode', () => {
    render(
      <PerformanceMonitor
        performanceMetrics={mockPerformanceMetrics}
        systemMetrics={mockSystemMetrics}
      />
    );

    // Click the Detailed button
    fireEvent.click(screen.getByText('Detailed'));

    // Check for detailed metrics
    expect(screen.getByText('Processing Time')).toBeInTheDocument();
    expect(screen.getByText('4.00s')).toBeInTheDocument();

    expect(screen.getByText('Audio Duration')).toBeInTheDocument();
    expect(screen.getByText('3.50s')).toBeInTheDocument();

    expect(screen.getByText('Total Interaction')).toBeInTheDocument();

    // Check for history sections
    expect(screen.getByText('Processing Time History')).toBeInTheDocument();
    expect(screen.getByText('CPU Usage History')).toBeInTheDocument();
  });

  it('switches back to basic mode when the Basic button is clicked', () => {
    render(
      <PerformanceMonitor
        performanceMetrics={mockPerformanceMetrics}
        systemMetrics={mockSystemMetrics}
      />
    );

    // First switch to detailed mode
    fireEvent.click(screen.getByText('Detailed'));

    // Then switch back to basic mode
    fireEvent.click(screen.getByText('Basic'));

    // Basic mode should now be active
    expect(screen.getByText('Basic')).toHaveClass('bg-primary-600');

    // Check for basic mode elements
    expect(screen.getAllByText('Processing Time').length).toBe(1);
    expect(screen.getByText('System Resources')).toBeInTheDocument();
  });
});
