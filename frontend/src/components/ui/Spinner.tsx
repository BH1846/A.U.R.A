import React from 'react';
import { Loader2 } from 'lucide-react';

export interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  color?: string;
  className?: string;
}

const sizeClasses = {
  sm: 'w-4 h-4',
  md: 'w-8 h-8',
  lg: 'w-12 h-12',
};

export const Spinner: React.FC<SpinnerProps> = ({
  size = 'md',
  color = '#63D7C7',
  className = '',
}) => {
  return (
    <Loader2
      className={`animate-spin ${sizeClasses[size]} ${className}`}
      style={{ color }}
    />
  );
};

export const LoadingScreen: React.FC<{ message?: string }> = ({
  message = 'Loading...',
}) => {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-neutral-light">
      <Spinner size="lg" />
      <p className="mt-4 text-lg text-neutral-dark/60">{message}</p>
    </div>
  );
};
