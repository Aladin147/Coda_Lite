import React from 'react';
import { render, screen } from '@testing-library/react';
import Layout from './Layout';
import { useConnectionState } from '../store/selectors';

// Mock the store selectors
jest.mock('../store/selectors', () => ({
  useConnectionState: jest.fn(),
}));

describe('Layout Component', () => {
  beforeEach(() => {
    // Default mock implementation
    (useConnectionState as jest.Mock).mockReturnValue({
      connected: true,
    });
  });

  test('renders with connected status', () => {
    render(
      <Layout>
        <div data-testid="test-child">Test Content</div>
      </Layout>
    );
    
    // Check that the header contains the title
    expect(screen.getByText('Coda Dashboard')).toBeInTheDocument();
    
    // Check that the connection status is displayed
    expect(screen.getByText('Connection:')).toBeInTheDocument();
    expect(screen.getByText('Connected')).toBeInTheDocument();
    
    // Check that the children are rendered
    expect(screen.getByTestId('test-child')).toBeInTheDocument();
    expect(screen.getByText('Test Content')).toBeInTheDocument();
    
    // Check that the footer is rendered
    const currentYear = new Date().getFullYear().toString();
    expect(screen.getByText(new RegExp(`Coda Dashboard v2.0 - © ${currentYear}`))).toBeInTheDocument();
  });

  test('renders with disconnected status', () => {
    (useConnectionState as jest.Mock).mockReturnValue({
      connected: false,
    });
    
    render(
      <Layout>
        <div>Test Content</div>
      </Layout>
    );
    
    // Check that the disconnected status is displayed
    expect(screen.getByText('Disconnected')).toBeInTheDocument();
  });
});
