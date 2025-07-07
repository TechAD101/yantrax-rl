import React from 'react';

interface BadgeProps {
  children: React.ReactNode;
  variant?: "default" | "secondary";
  className?: string;
}

export const Badge = ({ children, variant = "default", className = "" }: BadgeProps) => (
  <span className={`inline-block px-2 py-1 rounded text-xs font-semibold ${variant === "secondary" ? "bg-blue-800 text-white" : "bg-gray-500 text-white"} ${className}`}>
    {children}
  </span>
);
