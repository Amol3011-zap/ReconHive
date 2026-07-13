'use client';

import React from 'react';
import { Sidebar } from './Sidebar';
import { AICopilot } from './AICopilot';

interface MainLayoutProps {
  children: React.ReactNode;
  title?: string;
  subtitle?: string;
}

export function MainLayout({ children, title, subtitle }: MainLayoutProps) {
  return (
    <div className="min-h-screen bg-slate-950">
      <Sidebar />

      <main className="ml-64">
        {/* Header */}
        {(title || subtitle) && (
          <header className="border-b border-slate-700 bg-slate-900/50 px-8 py-6">
            {title && <h1 className="text-3xl font-bold text-slate-50">{title}</h1>}
            {subtitle && <p className="mt-1 text-slate-400">{subtitle}</p>}
          </header>
        )}

        {/* Content */}
        <div className="p-8">
          {children}
        </div>
      </main>

      <AICopilot />
    </div>
  );
}
