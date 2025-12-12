import React from 'react';

export interface CardProps {
  variant?: 'default' | 'elevated' | 'outlined';
  padding?: 'sm' | 'md' | 'lg';
  className?: string;
  children: React.ReactNode;
}

const variantClasses = {
  default: 'bg-white rounded-2xl shadow-soft',
  elevated: 'bg-white rounded-2xl shadow-medium hover:shadow-large transition-shadow duration-200',
  outlined: 'bg-white rounded-2xl border-2 border-neutral-dark/10',
};

const paddingClasses = {
  sm: 'p-4',
  md: 'p-6',
  lg: 'p-8',
};

export const Card: React.FC<CardProps> = ({
  variant = 'default',
  padding = 'md',
  className = '',
  children,
}) => {
  return (
    <div className={`${variantClasses[variant]} ${paddingClasses[padding]} ${className}`}>
      {children}
    </div>
  );
};
