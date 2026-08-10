interface BadgeProps {
  variant?: 'default' | 'admin' | 'user' | 'active' | 'blocked' | 'on' | 'off';
  children: React.ReactNode;
}

const variants = {
  default: 'bg-gray-100 text-gray-800',
  admin: 'bg-primary-100 text-primary-900',
  user: 'bg-gray-100 text-gray-800',
  active: 'bg-green-100 text-green-800',
  blocked: 'bg-red-100 text-red-800',
  on: 'bg-green-100 text-green-800',
  off: 'bg-red-100 text-red-800',
};

export function Badge({ variant = 'default', children }: BadgeProps) {
  return (
    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${variants[variant]}`}>
      {children}
    </span>
  );
}
