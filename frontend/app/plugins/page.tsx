'use client';

import React, { useState } from 'react';
import { MainLayout } from '@/components/MainLayout';

interface Plugin {
  id: string;
  name: string;
  version: string;
  status: 'healthy' | 'warning' | 'error';
  lastRun: string;
  targets: string;
}

const plugins: Plugin[] = [
  { id: '1', name: 'Nmap', version: '7.93', status: 'healthy', lastRun: '5 min ago', targets: 'IP ranges, CIDR' },
  { id: '2', name: 'Nuclei', version: '2.9.1', status: 'healthy', lastRun: '3 min ago', targets: 'Web apps, APIs' },
  { id: '3', name: 'HTTPX', version: '1.3.2', status: 'healthy', lastRun: '2 min ago', targets: 'Web servers' },
  { id: '4', name: 'Katana', version: '1.1.0', status: 'healthy', lastRun: '8 min ago', targets: 'Web crawling' },
  { id: '5', name: 'Amass', version: '4.0.0', status: 'healthy', lastRun: '10 min ago', targets: 'Subdomain enum' },
  { id: '6', name: 'DNSX', version: '1.1.6', status: 'healthy', lastRun: '1 min ago', targets: 'DNS queries' },
  { id: '7', name: 'Naabu', version: '2.1.5', status: 'warning', lastRun: '15 min ago', targets: 'Port scanning' },
  { id: '8', name: 'Subfinder', version: '2.6.0', status: 'healthy', lastRun: '7 min ago', targets: 'Subdomain enum' },
];

export default function PluginsPage() {
  return (
    <MainLayout title="Plugins" subtitle="Security scanning tools and adapters">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {plugins.map((plugin) => (
          <div key={plugin.id} className="rounded-lg border border-slate-700 bg-slate-950 p-4 hover:bg-slate-900 transition-colors">
            <div className="flex items-start justify-between mb-2">
              <h3 className="text-lg font-semibold text-slate-50">{plugin.name}</h3>
              <span className={`inline-block h-2 w-2 rounded-full ${
                plugin.status === 'healthy' ? 'bg-green-500' :
                plugin.status === 'warning' ? 'bg-yellow-500' :
                'bg-red-500'
              }`} />
            </div>

            <p className="text-xs text-slate-400 mb-3">v{plugin.version}</p>

            <div className="space-y-2 text-xs">
              <div>
                <p className="text-slate-500">Status</p>
                <p className="text-slate-300 capitalize">{plugin.status}</p>
              </div>
              <div>
                <p className="text-slate-500">Last Run</p>
                <p className="text-slate-300">{plugin.lastRun}</p>
              </div>
              <div>
                <p className="text-slate-500">Targets</p>
                <p className="text-slate-300">{plugin.targets}</p>
              </div>
            </div>

            <button className="mt-4 w-full rounded bg-purple-600/20 px-3 py-2 text-xs font-medium text-purple-400 hover:bg-purple-600/30">
              ⚙️ Configure
            </button>
          </div>
        ))}
      </div>
    </MainLayout>
  );
}
