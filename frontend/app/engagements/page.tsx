'use client';

import React, { useState } from 'react';
import { MainLayout } from '@/components/MainLayout';
import { Table } from '@/components/Table';

export default function EngagementsPage() {
  const [engagements] = useState([
    { id: '1', name: 'Acme Corp Internal Test', client: 'Acme Corp', status: 'Active', type: 'Penetration Test', started: '2026-07-06', ended: '2026-08-06' },
    { id: '2', name: 'Beta Finance Security Audit', client: 'Beta Finance', status: 'Active', type: 'Vulnerability Assessment', started: '2026-07-08', ended: '2026-07-28' },
    { id: '3', name: 'DataCorp Web App Assessment', client: 'DataCorp', status: 'Completed', type: 'Penetration Test', started: '2026-06-13', ended: '2026-06-30' },
    { id: '4', name: 'TechStart API Security Review', client: 'TechStart', status: 'Completed', type: 'Code Review', started: '2026-06-01', ended: '2026-06-15' },
  ]);

  return (
    <MainLayout title="Engagements" subtitle="Manage your security assessments and engagements">
      <div className="mb-6 flex items-center justify-between">
        <input
          type="text"
          placeholder="Search engagements..."
          className="rounded-lg border border-slate-700 bg-slate-900 px-4 py-2 text-slate-50 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-600 w-80"
        />
        <button className="rounded-lg bg-purple-600 px-6 py-2 font-medium text-white hover:bg-purple-700">
          ➕ New Engagement
        </button>
      </div>

      <Table
        columns={[
          { key: 'name', label: 'Engagement Name' },
          { key: 'client', label: 'Client' },
          { key: 'status', label: 'Status', render: (status) => <span className={`inline-block rounded px-2 py-1 text-xs font-semibold ${status === 'Active' ? 'bg-green-900/30 text-green-300' : 'bg-slate-900 text-slate-300'}`}>{status}</span> },
          { key: 'type', label: 'Type' },
          { key: 'started', label: 'Started' },
          { key: 'ended', label: 'Ends' },
        ]}
        data={engagements}
      />
    </MainLayout>
  );
}
