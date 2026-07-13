'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import React from 'react';

const menuItems = [
  { label: 'Dashboard', href: '/', icon: '📊' },
  { label: 'Engagements', href: '/engagements', icon: '📋' },
  { label: 'Assets', href: '/assets', icon: '🖥️' },
  { label: 'Scans', href: '/scans', icon: '🔍' },
  { label: 'Findings', href: '/findings', icon: '🚨' },
  { label: 'Evidence', href: '/evidence', icon: '📸' },
  { label: 'Reports', href: '/reports', icon: '📄' },
  { label: 'Settings', href: '/settings', icon: '⚙️' },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 border-r border-slate-700 bg-slate-950 p-4 overflow-y-auto">
      <div className="mb-8">
        <Link href="/" className="flex items-center gap-2 text-xl font-bold text-slate-50">
          <span>🔐</span>
          <span>ReconHive</span>
        </Link>
        <p className="mt-1 text-xs text-slate-400">v0.1-alpha</p>
      </div>

      <nav className="space-y-1">
        {menuItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors ${
                isActive
                  ? 'bg-purple-900 text-purple-100'
                  : 'text-slate-300 hover:bg-slate-800 hover:text-slate-100'
              }`}
            >
              <span>{item.icon}</span>
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="absolute bottom-4 left-4 right-4 border-t border-slate-700 pt-4">
        <div className="rounded-lg bg-slate-900 p-3">
          <p className="text-xs font-semibold text-slate-300">Quick Actions</p>
          <button className="mt-2 w-full rounded bg-purple-600 px-3 py-2 text-xs font-medium text-white hover:bg-purple-700">
            ➕ New Engagement
          </button>
        </div>
      </div>
    </aside>
  );
}
