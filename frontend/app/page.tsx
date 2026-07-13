'use client';

import React, { useState } from 'react';
import { MainLayout } from '@/components/MainLayout';
import { MetricCard } from '@/components/MetricCard';
import { ActivityTimeline } from '@/components/ActivityTimeline';
import { RiskChart } from '@/components/RiskChart';
import { Table } from '@/components/Table';
import Link from 'next/link';

export default function Dashboard() {
  const [stats] = useState({
    engagements: 12,
    assets: 4231,
    scans: 7,
    findings: 156,
    criticalFindings: 9,
    evidence: 156,
    aiInsights: 4,
  });

  const activities = [
    { id: '1', type: 'engagement_created' as const, title: 'Engagement "Acme Corp Internal Test" created', timestamp: new Date(Date.now() - 3 * 60000) },
    { id: '2', type: 'scan_started' as const, title: 'Scan "Nuclei - Web Scan" completed', timestamp: new Date(Date.now() - 15 * 60000) },
    { id: '3', type: 'evidence_uploaded' as const, title: 'Evidence uploaded: screenshot_20250713_1422.png', timestamp: new Date(Date.now() - 1 * 60000) },
    { id: '4', type: 'finding_created' as const, title: 'New finding: Exposed Admin Panel', severity: 'High', timestamp: new Date(Date.now() - 2 * 60000) },
    { id: '5', type: 'scan_started' as const, title: 'Scan "Subdomain Discovery" started', timestamp: new Date(Date.now() - 29 * 60000) },
  ];

  const scans = [
    { id: '1', name: 'Nuclei - Web Scan', target: 'app.acme.com', status: 'Running', progress: 79, worker: 'worker-2', duration: '00:15:32' },
    { id: '2', name: 'Subdomain Discovery', target: 'acme.com', status: 'Running', progress: 45, worker: 'worker-1', duration: '00:08:12' },
    { id: '3', name: 'Nmap - Full Scan', target: 'acme.com', status: 'Running', progress: 30, worker: 'worker-3', duration: '00:12:45' },
    { id: '4', name: 'DNS Enumeration', target: 'acme.com', status: 'Completed', progress: 100, worker: 'worker-1', duration: '00:05:21' },
    { id: '5', name: 'SSL/TLS Assessment', target: 'paymentapp.acme.com', status: 'Completed', progress: 100, worker: 'worker-2', duration: '00:03:18' },
  ];

  const topFindings = [
    { id: '1', title: 'Exposed Admin Panel', severity: 'High', count: 12 },
    { id: '2', title: 'Missing SPF Record', severity: 'Medium', count: 8 },
    { id: '3', title: 'Weak TLS Configuration', severity: 'High', count: 5 },
    { id: '4', title: 'Public S3 Bucket', severity: 'High', count: 3 },
    { id: '5', title: 'Information Disclosure', severity: 'Medium', count: 5 },
  ];

  const assets = [
    { type: 'Domain', count: 1245 },
    { type: 'IP Address', count: 312 },
    { type: 'Web App', count: 53 },
    { type: 'Cloud Assets', count: 156 },
  ];

  const evidence = [
    { type: 'Screenshots', count: 78 },
    { type: 'HTTP Responses', count: 42 },
    { type: 'Logs', count: 18 },
    { type: 'Other Files', count: 18 },
  ];

  const riskData = {
    CRITICAL: 9,
    HIGH: 27,
    MEDIUM: 48,
    LOW: 38,
    INFO: 34,
  };

  return (
    <MainLayout title="Dashboard" subtitle="Overview of your security assessments">
      {/* Metric Cards */}
      <div className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard label="Active Engagements" value={stats.engagements} trend={{ direction: 'up', percent: 20 }} icon="📋" color="blue" />
        <MetricCard label="Total Assets" value={`${(stats.assets / 1000).toFixed(1)}K`} trend={{ direction: 'up', percent: 12 }} icon="🖥️" color="cyan" />
        <MetricCard label="Scans Running" value={stats.scans} trend={{ direction: 'up', percent: 40 }} icon="🔍" color="green" />
        <MetricCard label="Total Findings" value={stats.findings} trend={{ direction: 'up', percent: 32 }} icon="🚨" color="red" />
        <MetricCard label="Critical Findings" value={stats.criticalFindings} trend={{ direction: 'down', percent: 5 }} icon="🔴" color="red" />
        <MetricCard label="Evidence Files" value={stats.evidence} trend={{ direction: 'up', percent: 8 }} icon="📸" color="purple" />
        <MetricCard label="AI Insights" value={stats.aiInsights} trend={{ direction: 'up', percent: 25 }} icon="🤖" color="amber" />
      </div>

      {/* Main Grid */}
      <div className="mb-8 grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Recent Activity */}
        <div className="rounded-lg border border-slate-700 bg-slate-950 p-6 lg:col-span-1">
          <h3 className="mb-4 text-lg font-semibold text-slate-50">Recent Activity</h3>
          <ActivityTimeline activities={activities} />
          <Link href="/activity" className="mt-4 inline-block text-sm text-purple-400 hover:text-purple-300">
            View all activity →
          </Link>
        </div>

        {/* Scan Overview */}
        <div className="lg:col-span-2">
          <Table
            title="Scan Overview"
            columns={[
              { key: 'name', label: 'Scan Name' },
              { key: 'target', label: 'Target' },
              { key: 'status', label: 'Status', render: (status) => <span className={`inline-block rounded px-2 py-1 text-xs font-semibold ${status === 'Running' ? 'bg-yellow-900/30 text-yellow-300' : 'bg-green-900/30 text-green-300'}`}>{status}</span> },
              { key: 'progress', label: 'Progress', render: (progress) => <div className="h-1.5 w-20 rounded-full bg-slate-700"><div className="h-full rounded-full bg-purple-500" style={{ width: `${progress}%` }} /></div> },
              { key: 'worker', label: 'Worker' },
              { key: 'duration', label: 'Duration' },
            ]}
            data={scans}
          />
        </div>
      </div>

      {/* Risk Overview + Findings + Assets */}
      <div className="mb-8 grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Risk Chart */}
        <div className="rounded-lg border border-slate-700 bg-slate-950 p-6">
          <h3 className="mb-4 text-lg font-semibold text-slate-50">Findings by Severity</h3>
          <RiskChart data={riskData} />
        </div>

        {/* Top Findings */}
        <div className="rounded-lg border border-slate-700 bg-slate-950 p-6">
          <h3 className="mb-4 text-lg font-semibold text-slate-50">Top Findings</h3>
          <div className="space-y-3">
            {topFindings.map((finding) => (
              <div key={finding.id} className="flex items-center justify-between rounded-lg bg-slate-900 p-3 hover:bg-slate-800 transition-colors cursor-pointer">
                <div>
                  <p className="text-sm font-medium text-slate-100">{finding.title}</p>
                  <span className={`inline-block mt-1 text-xs font-semibold px-2 py-0.5 rounded ${finding.severity === 'High' ? 'bg-red-900/30 text-red-300' : 'bg-yellow-900/30 text-yellow-300'}`}>{finding.severity}</span>
                </div>
                <span className="text-sm font-bold text-slate-400">{finding.count}</span>
              </div>
            ))}
          </div>
          <Link href="/findings" className="mt-4 inline-block text-sm text-purple-400 hover:text-purple-300">
            View all findings →
          </Link>
        </div>

        {/* Assets Summary */}
        <div className="rounded-lg border border-slate-700 bg-slate-950 p-6">
          <h3 className="mb-4 text-lg font-semibold text-slate-50">Assets Summary</h3>
          <div className="space-y-3">
            {assets.map((asset, idx) => (
              <div key={idx} className="flex items-center justify-between">
                <span className="text-sm text-slate-300">{asset.type}</span>
                <span className="text-lg font-bold text-slate-100">{asset.count}</span>
              </div>
            ))}
          </div>
          <div className="mt-4 rounded-lg bg-slate-900 p-3 text-center">
            <p className="text-sm font-bold text-slate-50">4,231</p>
            <p className="text-xs text-slate-400">Total Assets</p>
          </div>
        </div>
      </div>

      {/* Evidence Summary */}
      <div className="rounded-lg border border-slate-700 bg-slate-950 p-6">
        <h3 className="mb-6 text-lg font-semibold text-slate-50">Evidence Summary</h3>
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          {evidence.map((ev, idx) => (
            <div key={idx} className="rounded-lg bg-slate-900 p-4 text-center hover:bg-slate-800 transition-colors cursor-pointer">
              <p className="text-2xl font-bold text-slate-100">{ev.count}</p>
              <p className="mt-2 text-xs text-slate-400">{ev.type}</p>
            </div>
          ))}
        </div>
      </div>
    </MainLayout>
  );
}
