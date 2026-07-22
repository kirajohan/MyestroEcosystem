'use client';

import { ReactNode } from 'react';
import { AuthGuard } from '@/components/AuthGuard';
import { Sidebar } from '@/components/layout/Sidebar';
import { MobileSidebar } from '@/components/layout/MobileSidebar';
import { Header } from '@/components/layout/Header';

export default function ContentLayout({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <AuthGuard>
      <div className="flex h-screen bg-orange-50">
        {/* Desktop Sidebar */}
        <div className="hidden md:block w-60">
          <Sidebar />
        </div>

        {/* Mobile Sidebar */}
        <MobileSidebar />

        {/* Main Content */}
        <div className="flex-1 flex flex-col">
          <Header />
          <main className="flex-1 mt-16 overflow-auto p-4 md:p-6">
            {children}
          </main>
        </div>
      </div>
    </AuthGuard>
  );
}
