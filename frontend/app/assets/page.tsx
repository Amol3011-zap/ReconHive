'use client';

import React, { useState, useEffect } from 'react';
import { MainLayout } from '@/components/MainLayout';
import { Table } from '@/components/Table';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export default function AssetsPage() {
  const [assets, setAssets] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadAssets = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/assets`, {
          headers: { 'Authorization': 'Bearer demo-token' }
        });
        if (response.ok) {
          const data = await response.json();
          setAssets(data.data || []);
        }
      } catch (error) {
        console.error('Failed to load assets:', error);
        setAssets([]);
      } finally {
        setLoading(false);
      }
    };
    loadAssets();
  }, []);

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
