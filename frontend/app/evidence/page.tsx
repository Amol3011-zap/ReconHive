'use client';

import React, { useState, useEffect } from 'react';
import { MainLayout } from '@/components/MainLayout';
import { Table } from '@/components/Table';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export default function EvidencePage() {
  const [evidence, setEvidence] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadEvidence = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/evidence`, {
          headers: { 'Authorization': 'Bearer demo-token' }
        });
        if (response.ok) {
          const data = await response.json();
          setEvidence(data.data || []);
        }
      } catch (error) {
        console.error('Failed to load evidence:', error);
        setEvidence([]);
      } finally {
        setLoading(false);
      }
    };
    loadEvidence();
  }, []);

  return (
    <MainLayout title="Evidence" subtitle="Screenshots, logs, and proof of findings">
      <div className="mb-6 flex items-center justify-between">
        <input
          type="text"
          placeholder="Search evidence..."
          className="rounded-lg border border-slate-700 bg-slate-900 px-4 py-2 text-slate-50 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-600 w-80"
        />
        <button className="rounded-lg bg-purple-600 px-6 py-2 font-medium text-white hover:bg-purple-700">
          📤 Upload Evidence
        </button>
      </div>

      <Table
        columns={[
          { key: 'name', label: 'File Name' },
          { key: 'type', label: 'Type' },
          { key: 'size', label: 'Size' },
          { key: 'finding', label: 'Related Finding' },
          { key: 'uploaded', label: 'Uploaded' },
          { key: 'id', label: 'Actions', render: () => <button className="text-purple-400 hover:text-purple-300 text-sm">Download</button> },
        ]}
        data={evidence}
      />
    </MainLayout>
  );
}
