'use client';

import React, { useState } from 'react';
import { MainLayout } from '@/components/MainLayout';
import { Table } from '@/components/Table';

export default function ScansPage() {
  const [scans] = useState([
    { id: '1', name: 'Nuclei - Web Scan', plugin: 'Nuclei', target: 'app.acme.com', status: 'Running', progress: 79, started: '2026-07-13 10:00', worker: 'worker-2' },
    { id: '2', name: 'Subdomain Discovery', plugin: 'Subfinder', target: 'acme.com', status: 'Running', progress: 45, started: '2026-07-13 09:52', worker: 'worker-1' },
    { id: '3', name: 'Nmap - Full Scan', plugin: 'Nmap', target: 'acme.com', status: 'Running', progress: 30, started: '2026-07-13 09:47', worker: 'worker-3' },
    { id: '4', name: 'DNS Enumeration', plugin: 'dig', target: 'acme.com', status: 'Completed', progress: 100, started: '2026-07-13 08:00', worker: 'worker-1' },
    { id: '5', name: 'SSL/TLS Assessment', plugin: 'testssl.sh', target: 'paymentapp.acme.com', status: 'Completed', progress: 100, started: '2026-07-13 07:30', worker: 'worker-2' },
  ]);

  return (
    <MainLayout title="Scans" subtitle="Monitor and manage security scans">
      <div className="mb-6 flex items-center justify-between">
        <select className="rounded-lg border border-slate-700 bg-slate-900 px-4 py-2 text-slate-50 focus:outline-none focus:ring-2 focus:ring-purple-600">
          <option>All Status</option>
          <option>Running</option>
          <option>Completed</option>
          <option>Failed</option>
        </select>
        <button className="rounded-lg bg-purple-600 px-6 py-2 font-medium text-white hover:bg-purple-700">
          🚀 Launch Scan
        </button>
      </div>

      <Table
        columns={[
          { key: 'name', label: 'Scan Name' },
          { key: 'plugin', label: 'Plugin' },
          { key: 'target', label: 'Target' },
          { key: 'status', label: 'Status', render: (status) => <span className={`inline-block rounded px-2 py-1 text-xs font-semibold ${status === 'Running' ? 'bg-yellow-900/30 text-yellow-300' : 'bg-green-900/30 text-green-300'}`}>{status}</span> },
          { key: 'progress', label: 'Progress', render: (progress) => <div className="h-1.5 w-20 rounded-full bg-slate-700"><div className="h-full rounded-full bg-purple-500" style={{ width: `${progress}%` }} /></div> },
          { key: 'started', label: 'Started' },
          { key: 'worker', label: 'Worker' },
        ]}
        data={scans}
      />
    </MainLayout>
  );
}
