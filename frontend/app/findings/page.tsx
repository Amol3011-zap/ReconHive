'use client';

import React, { useState, useEffect } from 'react';
import { MainLayout } from '@/components/MainLayout';
import { Table } from '@/components/Table';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export default function FindingsPage() {
  const [findings, setFindings] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadFindings = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/findings`, {
          headers: { 'Authorization': 'Bearer demo-token' }
        });
        if (response.ok) {
          const data = await response.json();
          setFindings(data.data || []);
        }
      } catch (error) {
        console.error('Failed to load findings:', error);
        setFindings([]);
      } finally {
        setLoading(false);
      }
    };
    loadFindings();
  }, []);

  return (
    <MainLayout title="Findings" subtitle="Security vulnerabilities and issues">
      <div className="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
        <select className="rounded-lg border border-slate-700 bg-slate-900 px-4 py-2 text-slate-50 focus:outline-none focus:ring-2 focus:ring-purple-600">
          <option>All Severity</option>
          <option>CRITICAL</option>
          <option>HIGH</option>
          <option>MEDIUM</option>
        </select>
        <select className="rounded-lg border border-slate-700 bg-slate-900 px-4 py-2 text-slate-50 focus:outline-none focus:ring-2 focus:ring-purple-600">
          <option>All Status</option>
          <option>Open</option>
          <option>Confirmed</option>
          <option>Remediated</option>
        </select>
        <input
          type="text"
          placeholder="Search findings..."
          className="rounded-lg border border-slate-700 bg-slate-900 px-4 py-2 text-slate-50 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-600"
        />
      </div>

      <Table
        columns={[
          { key: 'title', label: 'Finding Title' },
          { key: 'severity', label: 'Severity', render: (severity) => <span className={`inline-block rounded px-2 py-1 text-xs font-semibold ${severity === 'CRITICAL' ? 'bg-red-900/30 text-red-300' : severity === 'HIGH' ? 'bg-orange-900/30 text-orange-300' : 'bg-yellow-900/30 text-yellow-300'}`}>{severity}</span> },
          { key: 'asset', label: 'Asset' },
          { key: 'status', label: 'Status', render: (status) => <span className={`inline-block rounded px-2 py-1 text-xs font-semibold ${status === 'Open' ? 'bg-red-900/30 text-red-300' : status === 'Confirmed' ? 'bg-yellow-900/30 text-yellow-300' : 'bg-green-900/30 text-green-300'}`}>{status}</span> },
          { key: 'cvss', label: 'CVSS' },
          { key: 'created', label: 'Created' },
        ]}
        data={findings}
      />
    </MainLayout>
  );
}
