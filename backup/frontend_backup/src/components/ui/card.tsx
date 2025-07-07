import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
}

export const Card = ({ children, className = "" }: CardProps) => (
  <div className={`rounded-xl p-4 bg-gray-800 shadow ${className}`}>
    {children}
  </div>
);
