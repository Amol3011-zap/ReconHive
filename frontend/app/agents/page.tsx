'use client';

import React, { useState } from 'react';
import { MainLayout } from '@/components/MainLayout';
import { Table } from '@/components/Table';

export default function AgentsPage() {
  const [agents] = useState([
    { id: '1', name: 'worker-1', status: 'Online', jobs: 3, queue: 5, cpu: '45%', memory: '2.1 GB' },
    { id: '2', name: 'worker-2', status: 'Online', jobs: 5, queue: 8, cpu: '68%', memory: '3.4 GB' },
    { id: '3', name: 'worker-3', status: 'Online', jobs: 2, queue: 3, cpu: '32%', memory: '1.8 GB' },
    { id: '4', name: 'worker-4', status: 'Offline', jobs: 0, queue: 0, cpu: '-', memory: '-' },
  ]);

  return (
    <MainLayout title="Agents" subtitle="Worker nodes and job distribution">
      <Table
        columns={[
          { key: 'name', label: 'Worker Name' },
          {
            key: 'status',
            label: 'Status',
            render: (status) => <span className={`inline-block rounded px-2 py-1 text-xs font-semibold ${status === 'Online' ? 'bg-green-900/30 text-green-300' : 'bg-slate-900 text-slate-400'}`}>{status}</span>
          },
          { key: 'jobs', label: 'Active Jobs' },
          { key: 'queue', label: 'Queued Jobs' },
          { key: 'cpu', label: 'CPU Usage' },
          { key: 'memory', label: 'Memory' },
        ]}
        data={agents}
      />
    </MainLayout>
  );
}
