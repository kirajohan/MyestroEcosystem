import { ButtonHTMLAttributes } from 'react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  isLoading?: boolean;
  children: React.ReactNode;
}

export function Button({ isLoading, disabled, children, className, ...props }: ButtonProps) {
  return (
    <button
      disabled={disabled || isLoading}
      className={`w-full px-4 py-2 bg-primary hover:bg-primary-hover text-white font-medium rounded-lg transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed ${className}`}
      {...props}
    >
      {isLoading ? 'Kirish...' : children}
    </button>
  );
}
