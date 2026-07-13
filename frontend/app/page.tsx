'use client';

import React, { useState, useEffect } from 'react';
import { MainLayout } from '@/components/MainLayout';
import { MetricCard } from '@/components/MetricCard';
import { ActivityTimeline } from '@/components/ActivityTimeline';
import { RiskChart } from '@/components/RiskChart';
import { Table } from '@/components/Table';
import Link from 'next/link';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export default function Dashboard() {
  // ALL DATA FROM DATABASE (ZERO HARDCODED VALUES)
  const [stats, setStats] = useState({
    engagements: 0,
    assets: 0,
    scans: 0,
    findings: 0,
    criticalFindings: 0,
    evidence: 0,
  });

  const [activities, setActivities] = useState<any[]>([]);
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadAllDashboardData();
  }, []);

  const loadAllDashboardData = async () => {
    try {
      setError(null);

      // Load stats (NO engagement filter - get all data)
      console.log('Fetching dashboard stats...');
      const statsResponse = await fetch(`${API_BASE_URL}/dashboard/stats`, {
        headers: { 'Authorization': 'Bearer demo-token' }
      });

      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        console.log('Stats data received:', statsData.data);
        setStats({
          engagements: statsData.data.engagements?.total || 0,
          assets: statsData.data.assets?.total || 0,
          scans: statsData.data.scans?.running || 0,
          findings: statsData.data.findings?.total || 0,
          criticalFindings: statsData.data.findings?.critical || 0,
          evidence: statsData.data.evidence?.total || 0,
        });
      } else {
        console.error('Stats API failed:', statsResponse.status, statsResponse.statusText);
        setError(`Stats API error: ${statsResponse.status}`);
      }

      // Load activities
      console.log('Fetching dashboard activity...');
      const activityResponse = await fetch(`${API_BASE_URL}/dashboard/activity?limit=5`, {
        headers: { 'Authorization': 'Bearer demo-token' }
      });

      if (activityResponse.ok) {
        const activityData = await activityResponse.json();
        const activitiesData = activityData.data.activities.map((a: any) => ({
          id: Math.random().toString(),
          type: a.type,
          title: a.title,
          timestamp: new Date(a.timestamp),
          icon: a.icon
        }));
        setActivities(activitiesData);
      }

      // Load complete dashboard data (findings, assets, evidence)
      const dashboardResponse = await fetch(`${API_BASE_URL}/dashboard/full`, {
        headers: { 'Authorization': 'Bearer demo-token' }
      });

      if (dashboardResponse.ok) {
        const fullData = await dashboardResponse.json();
        setDashboardData(fullData.data);
      }
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <MainLayout title="Dashboard" subtitle="Overview of your security assessments">
        <div className="text-center py-12 text-slate-400">Loading dashboard data...</div>
      </MainLayout>
    );
  }

  // Helper to render risk data (convert severity counts to chart format)
  const getRiskChartData = () => {
    if (!dashboardData?.findings_by_severity || typeof dashboardData.findings_by_severity === 'object' && 'message' in dashboardData.findings_by_severity) {
      return { CRITICAL: 0, HIGH: 0, MEDIUM: 0, LOW: 0, INFO: 0 };
    }
    return {
      CRITICAL: dashboardData.findings_by_severity?.CRITICAL || 0,
      HIGH: dashboardData.findings_by_severity?.HIGH || 0,
      MEDIUM: dashboardData.findings_by_severity?.MEDIUM || 0,
      LOW: dashboardData.findings_by_severity?.LOW || 0,
      INFO: dashboardData.findings_by_severity?.INFO || 0,
    };
  };

  const riskData = getRiskChartData();

  // Get scans for overview table
  const scans = dashboardData?.scans_overview || [];

  // Get top findings
  const topFindings = dashboardData?.top_findings || [];

  // Get asset summary
  const assetSummary = dashboardData?.asset_summary || {};

  // Get evidence summary
  const evidenceSummary = dashboardData?.evidence_summary || {};

  return (
    <MainLayout title="Dashboard" subtitle="Overview of your security assessments">
      {/* Error Banner - Show if API failed */}
      {error && (
        <div className="mb-6 rounded-lg border border-red-700 bg-red-900/20 p-4 text-red-300">
          <p className="text-sm">⚠️ {error}</p>
          <p className="text-xs text-red-400 mt-1">Showing zero values for all metrics. Please ensure the backend API is running at {API_BASE_URL}</p>
        </div>
      )}

      {/* Metric Cards - All from real database queries */}
      <div className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard label="Active Engagements" value={stats.engagements} trend={{ direction: 'up', percent: 0 }} icon="📋" color="blue" />
        <MetricCard label="Total Assets" value={stats.assets} trend={{ direction: 'up', percent: 0 }} icon="🖥️" color="cyan" />
        <MetricCard label="Scans Running" value={stats.scans} trend={{ direction: 'up', percent: 0 }} icon="🔍" color="green" />
        <MetricCard label="Total Findings" value={stats.findings} trend={{ direction: 'up', percent: 0 }} icon="🚨" color="red" />
        <MetricCard label="Critical Findings" value={stats.criticalFindings} trend={{ direction: 'down', percent: 0 }} icon="🔴" color="red" />
        <MetricCard label="Evidence Files" value={stats.evidence} trend={{ direction: 'up', percent: 0 }} icon="📸" color="purple" />
      </div>

      {/* Main Grid */}
      <div className="mb-8 grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Recent Activity - Real data from database */}
        <div className="rounded-lg border border-slate-700 bg-slate-950 p-6 lg:col-span-1">
          <h3 className="mb-4 text-lg font-semibold text-slate-50">Recent Activity</h3>
          {activities.length > 0 ? (
            <>
              <ActivityTimeline activities={activities} />
              <Link href="/activity" className="mt-4 inline-block text-sm text-purple-400 hover:text-purple-300">
                View all activity →
              </Link>
            </>
          ) : (
            <p className="text-sm text-slate-400">No activity yet.</p>
          )}
        </div>

        {/* Scan Overview - Real scans from database */}
        <div className="lg:col-span-2">
          {scans.length > 0 && !scans[0].message ? (
            <Table
              title="Scan Overview"
              columns={[
                { key: 'name', label: 'Scan Name' },
                { key: 'status', label: 'Status', render: (status) => <span className={`inline-block rounded px-2 py-1 text-xs font-semibold ${status === 'running' ? 'bg-yellow-900/30 text-yellow-300' : 'bg-green-900/30 text-green-300'}`}>{status}</span> },
                { key: 'progress', label: 'Progress', render: (progress) => <div className="h-1.5 w-20 rounded-full bg-slate-700"><div className="h-full rounded-full bg-purple-500" style={{ width: `${progress}%` }} /></div> },
                { key: 'worker', label: 'Worker' },
                { key: 'duration_seconds', label: 'Duration', render: (duration) => duration ? `${Math.floor(duration / 60)}m` : '-' },
              ]}
              data={scans}
            />
          ) : (
            <div className="rounded-lg border border-slate-700 bg-slate-950 p-6">
              <h3 className="mb-4 text-lg font-semibold text-slate-50">Scan Overview</h3>
              <p className="text-sm text-slate-400">No scans yet.</p>
            </div>
          )}
        </div>
      </div>

      {/* Risk, Findings, Assets - All real data from database */}
      <div className="mb-8 grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Findings by Severity - Real data from database query */}
        <div className="rounded-lg border border-slate-700 bg-slate-950 p-6">
          <h3 className="mb-4 text-lg font-semibold text-slate-50">Findings by Severity</h3>
          {Object.keys(riskData).length > 0 && (Object.values(riskData) as number[]).some(v => v > 0) ? (
            <RiskChart data={riskData} />
          ) : (
            <p className="text-sm text-slate-400">No findings yet.</p>
          )}
        </div>

        {/* Top Findings - Real data from database (grouped by title) */}
        <div className="rounded-lg border border-slate-700 bg-slate-950 p-6">
          <h3 className="mb-4 text-lg font-semibold text-slate-50">Top Findings</h3>
          {topFindings.length > 0 && !topFindings[0].message ? (
            <div className="space-y-3">
              {topFindings.slice(0, 5).map((finding: any) => (
                <div key={finding.title} className="flex items-center justify-between rounded-lg bg-slate-900 p-3 hover:bg-slate-800 transition-colors cursor-pointer">
                  <div>
                    <p className="text-sm font-medium text-slate-100">{finding.title}</p>
                    <span className={`inline-block mt-1 text-xs font-semibold px-2 py-0.5 rounded ${
                      finding.severity === 'critical' || finding.severity === 'high' ? 'bg-red-900/30 text-red-300' :
                      finding.severity === 'medium' ? 'bg-yellow-900/30 text-yellow-300' :
                      'bg-slate-900 text-slate-400'
                    }`}>
                      {finding.severity}
                    </span>
                  </div>
                  <span className="text-sm font-bold text-slate-400">{finding.count}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-slate-400">No findings available.</p>
          )}
          <Link href="/findings" className="mt-4 inline-block text-sm text-purple-400 hover:text-purple-300">
            View all findings →
          </Link>
        </div>

        {/* Assets Summary - Real data from database (grouped by type) */}
        <div className="rounded-lg border border-slate-700 bg-slate-950 p-6">
          <h3 className="mb-4 text-lg font-semibold text-slate-50">Assets Summary</h3>
          {Object.keys(assetSummary).length > 0 && !assetSummary.message ? (
            <>
              <div className="space-y-3">
                {Object.entries(assetSummary).map(([type, count]: [string, any]) => (
                  type !== 'total' && (
                    <div key={type} className="flex items-center justify-between">
                      <span className="text-sm text-slate-300 capitalize">{type.replace(/_/g, ' ')}</span>
                      <span className="text-lg font-bold text-slate-100">{count}</span>
                    </div>
                  )
                ))}
              </div>
              {assetSummary.total && (
                <div className="mt-4 rounded-lg bg-slate-900 p-3 text-center">
                  <p className="text-sm font-bold text-slate-50">{assetSummary.total}</p>
                  <p className="text-xs text-slate-400">Total Assets</p>
                </div>
              )}
            </>
          ) : (
            <p className="text-sm text-slate-400">No assets found.</p>
          )}
        </div>
      </div>

      {/* Evidence Summary - Real data from database (grouped by type) */}
      <div className="rounded-lg border border-slate-700 bg-slate-950 p-6">
        <h3 className="mb-6 text-lg font-semibold text-slate-50">Evidence Summary</h3>
        {Object.keys(evidenceSummary).length > 0 && !evidenceSummary.message ? (
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            {Object.entries(evidenceSummary).map(([type, count]: [string, any]) => (
              type !== 'total' && (
                <div key={type} className="rounded-lg bg-slate-900 p-4 text-center hover:bg-slate-800 transition-colors cursor-pointer">
                  <p className="text-2xl font-bold text-slate-100">{count}</p>
                  <p className="mt-2 text-xs text-slate-400 capitalize">{type.replace(/_/g, ' ')}</p>
                </div>
              )
            ))}
          </div>
        ) : (
          <p className="text-sm text-slate-400">Evidence collection not configured.</p>
        )}
      </div>
    </MainLayout>
  );
}
