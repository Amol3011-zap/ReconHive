'use client';

import React, { useState, useEffect } from 'react';
import { MainLayout } from '@/components/MainLayout';
import { Table } from '@/components/Table';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export default function EngagementsPage() {
  const [engagements, setEngagements] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadEngagements = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/engagements`, {
          headers: { 'Authorization': 'Bearer demo-token' }
        });
        if (response.ok) {
          const data = await response.json();
          setEngagements(data.data || []);
        }
      } catch (error) {
        console.error('Failed to load engagements:', error);
        setEngagements([]);
      } finally {
        setLoading(false);
      }
    };
    loadEngagements();
  }, []);

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
