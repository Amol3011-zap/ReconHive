'use client';

import React, { useState, useEffect } from 'react';
import { MainLayout } from '@/components/MainLayout';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export default function ReportsPage() {
  const [reports, setReports] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadReports = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/reports`, {
          headers: { 'Authorization': 'Bearer demo-token' }
        });
        if (response.ok) {
          const data = await response.json();
          setReports(data.data || []);
        }
      } catch (error) {
        console.error('Failed to load reports:', error);
        setReports([]);
      } finally {
        setLoading(false);
      }
    };
    loadReports();
  }, []);

  return (
    <MainLayout title="Reports" subtitle="Generate and download assessment reports">
      <div className="mb-6 flex items-center justify-between">
        <input
          type="text"
          placeholder="Search reports..."
          className="rounded-lg border border-slate-700 bg-slate-900 px-4 py-2 text-slate-50 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-600 w-80"
        />
        <button className="rounded-lg bg-purple-600 px-6 py-2 font-medium text-white hover:bg-purple-700">
          📝 Generate Report
        </button>
      </div>

      <div className="space-y-4">
        {reports.map((report) => (
          <div key={report.id} className="rounded-lg border border-slate-700 bg-slate-950 p-6 hover:bg-slate-900/50 transition-colors">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="text-lg font-semibold text-slate-50">{report.name}</h3>
                <p className="mt-1 text-sm text-slate-400">
                  Engagement: <span className="text-slate-300">{report.engagement}</span>
                </p>
                <div className="mt-3 flex items-center gap-4">
                  <span className="text-xs text-slate-400">
                    Created: <span className="text-slate-300">{report.created}</span>
                  </span>
                  <span className="rounded bg-red-900/30 px-2 py-1 text-xs font-semibold text-red-300">
                    {report.findings} Findings
                  </span>
                </div>
                <div className="mt-2 flex flex-wrap gap-2">
                  {report.sections.map((section) => (
                    <span key={section} className="rounded bg-slate-800 px-2 py-1 text-xs text-slate-300">
                      {section}
                    </span>
                  ))}
                </div>
              </div>
              <div className="flex flex-col gap-2">
                <button className="rounded bg-purple-600 px-4 py-2 text-sm font-medium text-white hover:bg-purple-700">
                  📥 PDF
                </button>
                <button className="rounded border border-slate-700 px-4 py-2 text-sm font-medium text-slate-300 hover:bg-slate-800">
                  📋 MD
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </MainLayout>
  );
}
