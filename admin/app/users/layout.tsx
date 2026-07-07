import { Sidebar } from '@/components/layout/Sidebar';

export default function UsersLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="ml-60 flex-1 p-6">{children}</main>
    </div>
  );
}