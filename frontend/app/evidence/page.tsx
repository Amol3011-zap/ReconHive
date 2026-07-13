'use client';

import React, { useState } from 'react';
import { MainLayout } from '@/components/MainLayout';
import { Table } from '@/components/Table';

export default function EvidencePage() {
  const [evidence] = useState([
    { id: '1', name: 'screenshot_20250713_1422.png', type: 'Screenshot', size: '2.3 MB', finding: 'Exposed Admin Panel', uploaded: '2026-07-13 14:22' },
    { id: '2', name: 'http_response_sql_injection.json', type: 'HTTP Response', size: '156 KB', finding: 'SQL Injection in Search', uploaded: '2026-07-12 10:15' },
    { id: '3', name: 'dns_enumeration_results.txt', type: 'Log', size: '45 KB', finding: 'DNS Enumeration', uploaded: '2026-07-11 09:30' },
    { id: '4', name: 'nmap_scan_results.xml', type: 'XML', size: '234 KB', finding: 'Network Scan', uploaded: '2026-07-10 16:45' },
    { id: '5', name: 'api_response_401.json', type: 'JSON', size: '89 KB', finding: 'Missing Authentication', uploaded: '2026-07-09 13:20' },
  ]);

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
