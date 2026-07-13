'use client';

import React, { useState } from 'react';
import { MainLayout } from '@/components/MainLayout';
import { Table } from '@/components/Table';

export default function SchedulesPage() {
  const [schedules] = useState([
    { id: '1', name: 'Daily Scan - Acme Corp', engagement: 'Acme Corp Internal Test', frequency: 'Daily', nextRun: '2026-07-14 02:00', status: 'Active', lastRun: '2026-07-13 02:15' },
    { id: '2', name: 'Weekly Full Scan - Beta Finance', engagement: 'Beta Finance Security Audit', frequency: 'Weekly', nextRun: '2026-07-20 10:00', status: 'Active', lastRun: '2026-07-13 10:30' },
    { id: '3', name: 'Hourly Web Scan - DataCorp', engagement: 'DataCorp Web App Assessment', frequency: 'Hourly', nextRun: '2026-07-13 15:00', status: 'Paused', lastRun: '2026-07-13 14:00' },
  ]);

  return (
    <MainLayout title="Schedules" subtitle="Automated scan scheduling and management">
      <div className="mb-6 flex items-center justify-between">
        <input
          type="text"
          placeholder="Search schedules..."
          className="rounded-lg border border-slate-700 bg-slate-900 px-4 py-2 text-slate-50 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-600 w-80"
        />
        <button className="rounded-lg bg-purple-600 px-6 py-2 font-medium text-white hover:bg-purple-700">
          ⏱️ New Schedule
        </button>
      </div>

      <Table
        columns={[
          { key: 'name', label: 'Schedule Name' },
          { key: 'engagement', label: 'Engagement' },
          { key: 'frequency', label: 'Frequency' },
          { key: 'nextRun', label: 'Next Run' },
          { key: 'status', label: 'Status', render: (status) => <span className={`inline-block rounded px-2 py-1 text-xs font-semibold ${status === 'Active' ? 'bg-green-900/30 text-green-300' : 'bg-yellow-900/30 text-yellow-300'}`}>{status}</span> },
          { key: 'lastRun', label: 'Last Run' },
        ]}
        data={schedules}
      />
    </MainLayout>
  );
}
