import React from 'react';
import { render, screen } from '@testing-library/react';
import Avatar from './Avatar';
import { useCodaMode } from '../store/selectors';

// Mock the store selectors
jest.mock('../store/selectors', () => ({
  useCodaMode: jest.fn(),
}));

describe('Avatar Component', () => {
  beforeEach(() => {
    // Default mock implementation
    (useCodaMode as jest.Mock).mockReturnValue({
      mode: 'idle',
      emotionContext: 'neutral',
    });
  });

  test('renders with idle mode and neutral emotion', () => {
    render(<Avatar />);
    
    // Check that the avatar displays the correct mode and emotion
    expect(screen.getByText(/Mode:/i)).toBeInTheDocument();
    expect(screen.getByText(/idle/i)).toBeInTheDocument();
    expect(screen.getByText(/Emotion:/i)).toBeInTheDocument();
    expect(screen.getByText(/neutral/i)).toBeInTheDocument();
  });

  test('renders with listening mode', () => {
    (useCodaMode as jest.Mock).mockReturnValue({
      mode: 'listening',
      emotionContext: 'neutral',
    });
    
    render(<Avatar />);
    
    expect(screen.getByText(/listening/i)).toBeInTheDocument();
    
    // Check that the avatar has the correct class
    const avatarElement = screen.getByText('C').closest('div');
    expect(avatarElement).toHaveClass('avatar-listening');
  });

  test('renders with thinking mode', () => {
    (useCodaMode as jest.Mock).mockReturnValue({
      mode: 'thinking',
      emotionContext: 'neutral',
    });
    
    render(<Avatar />);
    
    expect(screen.getByText(/thinking/i)).toBeInTheDocument();
    
    // Check that the avatar has the correct class
    const avatarElement = screen.getByText('C').closest('div');
    expect(avatarElement).toHaveClass('avatar-thinking');
  });

  test('renders with speaking mode', () => {
    (useCodaMode as jest.Mock).mockReturnValue({
      mode: 'speaking',
      emotionContext: 'neutral',
    });
    
    render(<Avatar />);
    
    expect(screen.getByText(/speaking/i)).toBeInTheDocument();
    
    // Check that the avatar has the correct class
    const avatarElement = screen.getByText('C').closest('div');
    expect(avatarElement).toHaveClass('avatar-speaking');
  });

  test('renders with error mode', () => {
    (useCodaMode as jest.Mock).mockReturnValue({
      mode: 'error',
      emotionContext: 'neutral',
    });
    
    render(<Avatar />);
    
    expect(screen.getByText(/error/i)).toBeInTheDocument();
    
    // Check that the avatar has the correct class
    const avatarElement = screen.getByText('C').closest('div');
    expect(avatarElement).toHaveClass('avatar-error');
  });

  test('emotion affects avatar appearance when idle', () => {
    (useCodaMode as jest.Mock).mockReturnValue({
      mode: 'idle',
      emotionContext: 'concerned',
    });
    
    render(<Avatar />);
    
    expect(screen.getByText(/concerned/i)).toBeInTheDocument();
    
    // Check that the avatar has the correct class (should use thinking style for concerned)
    const avatarElement = screen.getByText('C').closest('div');
    expect(avatarElement).toHaveClass('avatar-thinking');
  });
});
