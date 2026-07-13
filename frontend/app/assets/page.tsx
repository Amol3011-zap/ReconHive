'use client';

import React, { useState } from 'react';
import { MainLayout } from '@/components/MainLayout';
import { Table } from '@/components/Table';

export default function AssetsPage() {
  const [assets] = useState([
    { id: '1', name: 'app.acme.com', type: 'Web App', criticality: 'Critical', status: 'Active', tags: 'production, public' },
    { id: '2', name: 'api.acme.com', type: 'API', criticality: 'Critical', status: 'Active', tags: 'production, payment' },
    { id: '3', name: 'mail.acme.com', type: 'Mail Server', criticality: 'High', status: 'Active', tags: 'internal, critical' },
    { id: '4', name: 'paymentapp.acme.com', type: 'Web App', criticality: 'Critical', status: 'Active', tags: 'production, payment' },
    { id: '5', name: 'db.internal', type: 'Database', criticality: 'High', status: 'Active', tags: 'internal, database' },
    { id: '6', name: 'vpn.acme.com', type: 'VPN Server', criticality: 'High', status: 'Active', tags: 'internal, access' },
  ]);

  return (
    <MainLayout title="Assets" subtitle="Inventory of all assessed assets">
      <div className="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
        <select className="rounded-lg border border-slate-700 bg-slate-900 px-4 py-2 text-slate-50 focus:outline-none focus:ring-2 focus:ring-purple-600">
          <option>All Types</option>
          <option>Web App</option>
          <option>API</option>
          <option>Database</option>
        </select>
        <select className="rounded-lg border border-slate-700 bg-slate-900 px-4 py-2 text-slate-50 focus:outline-none focus:ring-2 focus:ring-purple-600">
          <option>All Criticality</option>
          <option>Critical</option>
          <option>High</option>
          <option>Medium</option>
        </select>
        <input
          type="text"
          placeholder="Search assets..."
          className="rounded-lg border border-slate-700 bg-slate-900 px-4 py-2 text-slate-50 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-600"
        />
      </div>

      <Table
        columns={[
          { key: 'name', label: 'Asset Name' },
          { key: 'type', label: 'Type' },
          { key: 'criticality', label: 'Criticality', render: (crit) => <span className={`inline-block rounded px-2 py-1 text-xs font-semibold ${crit === 'Critical' ? 'bg-red-900/30 text-red-300' : 'bg-orange-900/30 text-orange-300'}`}>{crit}</span> },
          { key: 'status', label: 'Status', render: (status) => <span className="inline-block rounded px-2 py-1 text-xs font-semibold bg-green-900/30 text-green-300">{status}</span> },
          { key: 'tags', label: 'Tags' },
        ]}
        data={assets}
      />
    </MainLayout>
  );
}
