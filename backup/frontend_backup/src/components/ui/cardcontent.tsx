import React from 'react';

interface CardContentProps {
  children: React.ReactNode;
}

export const CardContent = ({ children }: CardContentProps) => (
  <div className="p-2">
    {children}
  </div>
);
