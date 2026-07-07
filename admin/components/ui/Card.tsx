import { HTMLAttributes } from 'react';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

export function Card({ className, children, ...props }: CardProps) {
  return (
    <div
      className={`bg-white rounded-lg shadow-lg p-8 ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}
