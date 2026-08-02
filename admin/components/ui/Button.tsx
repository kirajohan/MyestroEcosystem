import { ButtonHTMLAttributes } from 'react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  isLoading?: boolean;
  children: React.ReactNode;
}

export function Button({ isLoading, disabled, children, className, ...props }: ButtonProps) {
  return (
    <button
      disabled={disabled || isLoading}
      className={`w-full px-4 py-2 bg-primary hover:bg-primary-700 active:scale-[0.98] active:opacity-90 text-white font-medium rounded-lg transition-all duration-150 ease-in-out hover:shadow-lg hover:shadow-primary-500/25 focus:outline-none focus:ring-2 focus:ring-primary-600 focus:ring-offset-2 disabled:bg-dark-200 disabled:cursor-not-allowed disabled:hover:shadow-none disabled:active:scale-100 ${className}`}
      {...props}
    >
      {isLoading ? (
        <span className="flex items-center justify-center gap-2">
          <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          Yuklanmoqda...
        </span>
      ) : children}
    </button>
  );
}
