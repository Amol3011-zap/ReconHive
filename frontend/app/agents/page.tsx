'use client';

import React, { useState, useEffect } from 'react';
import { MainLayout } from '@/components/MainLayout';
import { Table } from '@/components/Table';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export default function AgentsPage() {
  const [agents, setAgents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadWorkers();
  }, []);

  const loadWorkers = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/workers`, {
        headers: { 'Authorization': 'Bearer demo-token' }
      });
      if (response.ok) {
        const data = await response.json();
        const workersData = data.data.map((w: any) => ({
          id: w.id,
          name: w.name,
          status: w.status.charAt(0).toUpperCase() + w.status.slice(1),
          jobs: w.active_jobs,
          queue: w.queue_depth,
          cpu: `${w.cpu_usage.toFixed(1)}%`,
          memory: `${w.memory_usage.toFixed(1)}%`
        }));
        setAgents(workersData);
      } else {
        loadMockWorkers();
      }
    } catch (error) {
      console.error('Failed to load workers:', error);
      loadMockWorkers();
    } finally {
      setLoading(false);
    }
  };

  const loadMockWorkers = () => {
    setAgents([
      { id: '1', name: 'recon-worker-1', status: 'Online', jobs: 2, queue: 3, cpu: '45%', memory: '2.1 GB' },
      { id: '2', name: 'recon-worker-2', status: 'Online', jobs: 3, queue: 5, cpu: '68%', memory: '3.4 GB' },
      { id: '3', name: 'nuclei-worker', status: 'Online', jobs: 1, queue: 2, cpu: '32%', memory: '1.8 GB' },
      { id: '4', name: 'evidence-worker', status: 'Offline', jobs: 0, queue: 0, cpu: '-', memory: '-' },
    ]);
  };

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
