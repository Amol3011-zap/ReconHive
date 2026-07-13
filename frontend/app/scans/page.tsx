'use client';

import React, { useState, useEffect } from 'react';
import { MainLayout } from '@/components/MainLayout';
import { Modal } from '@/components/Modal';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export default function ScansPage() {
  const [scans, setScans] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showNewScan, setShowNewScan] = useState(false);
  const [selectedScan, setSelectedScan] = useState<any | null>(null);
  const [scanDetails, setScanDetails] = useState<any | null>(null);
  const [engagementId] = useState('550e8400-e29b-41d4-a716-446655440000');

  useEffect(() => {
    loadScans();
    const interval = setInterval(loadScans, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadScans = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/scans?engagement_id=${engagementId}`, {
        headers: { 'Authorization': 'Bearer demo-token' }
      });
      if (response.ok) {
        const data = await response.json();
        setScans(data.data || []);
      } else {
        loadMockScans();
      }
    } catch (error) {
      console.error('Failed to load scans:', error);
      loadMockScans();
    } finally {
      setLoading(false);
    }
  };

  const loadMockScans = () => {
    setScans([
      {
        id: '1',
        name: 'Nuclei - Web Scan',
        plugin_names: ['Nuclei'],
        status: 'running',
        progress_percent: 79,
        started_at: new Date(Date.now() - 6300000).toISOString(),
        duration_seconds: 0,
        worker_id: 'worker-2',
        current_stage: 'Scanning',
        target_id: 'acme.com'
      },
      {
        id: '2',
        name: 'Subdomain Discovery',
        plugin_names: ['Subfinder'],
        status: 'running',
        progress_percent: 45,
        started_at: new Date(Date.now() - 5700000).toISOString(),
        duration_seconds: 0,
        worker_id: 'worker-1',
        current_stage: 'Scanning',
        target_id: 'acme.com'
      },
      {
        id: '3',
        name: 'DNS Enumeration',
        plugin_names: ['dig'],
        status: 'completed',
        progress_percent: 100,
        started_at: new Date(Date.now() - 16000000).toISOString(),
        duration_seconds: 2732,
        worker_id: 'worker-1',
        current_stage: 'Completed',
        target_id: 'acme.com'
      }
    ]);
  };

  const loadScanDetails = async (scanId: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/scans/${scanId}/details`, {
        headers: { 'Authorization': 'Bearer demo-token' }
      });
      if (response.ok) {
        const data = await response.json();
        setScanDetails(data.data);
      }
    } catch (error) {
      console.error('Failed to load scan details:', error);
    }
  };

  const startScan = async (scanId: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/scans/${scanId}/start`, {
        method: 'POST',
        headers: { 'Authorization': 'Bearer demo-token' }
      });
      if (response.ok) {
        loadScans();
      }
    } catch (error) {
      console.error('Failed to start scan:', error);
    }
  };

  const simulateProgress = async (scanId: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/scans/${scanId}/progress`, {
        method: 'POST',
        headers: { 'Authorization': 'Bearer demo-token' }
      });
      if (response.ok) {
        loadScans();
        loadScanDetails(scanId);
      }
    } catch (error) {
      console.error('Failed to update progress:', error);
    }
  };

  const handleScanRowClick = async (scan: any) => {
    setSelectedScan(scan);
    await loadScanDetails(scan.id);
  };

  return (
    <MainLayout title="Scans" subtitle="Monitor and manage security scans">
      <div className="mb-6 flex items-center justify-between">
        <select className="rounded-lg border border-slate-700 bg-slate-900 px-4 py-2 text-slate-50 focus:outline-none focus:ring-2 focus:ring-purple-600">
          <option>All Status</option>
          <option>running</option>
          <option>completed</option>
          <option>failed</option>
        </select>
        <button
          onClick={() => setShowNewScan(true)}
          className="rounded-lg bg-purple-600 px-6 py-2 font-medium text-white hover:bg-purple-700">
          🚀 Launch Scan
        </button>
      </div>

      {loading ? (
        <div className="text-center py-8 text-slate-400">Loading scans...</div>
      ) : scans.length === 0 ? (
        <div className="text-center py-8 text-slate-400">No scans found</div>
      ) : (
        <div className="rounded-lg border border-slate-700 bg-slate-950 overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-700 bg-slate-900">
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">Scan Name</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">Plugin</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">Status</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">Progress</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">Duration</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">Worker</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">Actions</th>
              </tr>
            </thead>
            <tbody>
              {scans.map((scan: any) => (
                <tr
                  key={scan.id}
                  className="border-b border-slate-800 hover:bg-slate-900/50 transition-colors cursor-pointer"
                  onClick={() => handleScanRowClick(scan)}
                >
                  <td className="px-6 py-3 text-sm text-slate-300 font-medium">{scan.name}</td>
                  <td className="px-6 py-3 text-sm text-slate-300">{scan.plugin_names?.[0] || 'N/A'}</td>
                  <td className="px-6 py-3 text-sm">
                    <span className={`inline-block rounded px-2 py-1 text-xs font-semibold ${
                      scan.status === 'running' ? 'bg-yellow-900/30 text-yellow-300' :
                      scan.status === 'completed' ? 'bg-green-900/30 text-green-300' :
                      'bg-red-900/30 text-red-300'
                    }`}>{scan.status}</span>
                  </td>
                  <td className="px-6 py-3 text-sm">
                    <div className="flex items-center gap-2">
                      <div className="h-1.5 w-16 rounded-full bg-slate-700">
                        <div className="h-full rounded-full bg-purple-500" style={{ width: `${scan.progress_percent}%` }} />
                      </div>
                      <span className="text-xs text-slate-400">{scan.progress_percent}%</span>
                    </div>
                  </td>
                  <td className="px-6 py-3 text-sm text-slate-300">{scan.duration_seconds ? `${Math.floor(scan.duration_seconds / 60)}m` : '-'}</td>
                  <td className="px-6 py-3 text-sm text-slate-300">{scan.worker_id || '-'}</td>
                  <td className="px-6 py-3 text-sm" onClick={(e) => e.stopPropagation()}>
                    {scan.status === 'queued' && (
                      <button
                        onClick={() => startScan(scan.id)}
                        className="text-xs bg-blue-600 px-2 py-1 rounded hover:bg-blue-700"
                      >
                        Start
                      </button>
                    )}
                    {scan.status === 'running' && (
                      <button
                        onClick={() => simulateProgress(scan.id)}
                        className="text-xs bg-green-600 px-2 py-1 rounded hover:bg-green-700"
                      >
                        Progress
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Scan Details Modal */}
      {selectedScan && (
        <Modal
          isOpen={!!selectedScan}
          onClose={() => { setSelectedScan(null); setScanDetails(null); }}
          title={`${selectedScan.name} - Details`}
        >
          <div className="space-y-4">
            <div>
              <h4 className="text-sm font-semibold text-slate-50 mb-2">Status</h4>
              <p className="text-slate-300">{selectedScan.status}</p>
            </div>

            <div>
              <h4 className="text-sm font-semibold text-slate-50 mb-2">Progress</h4>
              <div className="flex items-center gap-2">
                <div className="h-2 w-full rounded-full bg-slate-700">
                  <div className="h-full rounded-full bg-purple-500" style={{ width: `${selectedScan.progress_percent}%` }} />
                </div>
                <span className="text-xs text-slate-400">{selectedScan.progress_percent}%</span>
              </div>
            </div>

            <div>
              <h4 className="text-sm font-semibold text-slate-50 mb-2">Current Stage</h4>
              <p className="text-slate-300">{selectedScan.current_stage}</p>
            </div>

            {scanDetails?.jobs?.length > 0 && (
              <div>
                <h4 className="text-sm font-semibold text-slate-50 mb-2">Execution Logs</h4>
                <div className="bg-slate-900 rounded p-3 h-40 overflow-y-auto text-xs font-mono text-slate-300 space-y-1">
                  {scanDetails.jobs[0].logs?.map((log: string, idx: number) => (
                    <div key={idx}>{log}</div>
                  ))}
                </div>
              </div>
            )}

            {scanDetails?.findings?.length > 0 && (
              <div>
                <h4 className="text-sm font-semibold text-slate-50 mb-2">Findings</h4>
                <div className="space-y-2">
                  {scanDetails.findings.map((f: any) => (
                    <div key={f.id} className="text-xs bg-slate-900 p-2 rounded">
                      <p className="text-slate-300">{f.title}</p>
                      <p className="text-slate-400">{f.severity}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {scanDetails?.evidence?.length > 0 && (
              <div>
                <h4 className="text-sm font-semibold text-slate-50 mb-2">Evidence</h4>
                <div className="space-y-2">
                  {scanDetails.evidence.map((e: any) => (
                    <div key={e.id} className="text-xs bg-slate-900 p-2 rounded text-slate-300">
                      {e.name}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </Modal>
      )}

      {/* New Scan Modal */}
      <Modal
        isOpen={showNewScan}
        onClose={() => setShowNewScan(false)}
        title="Launch New Scan"
        actions={
          <div className="flex gap-2 w-full">
            <button
              onClick={() => setShowNewScan(false)}
              className="flex-1 rounded border border-slate-600 px-4 py-2 text-sm font-medium text-slate-300 hover:bg-slate-800"
            >
              Cancel
            </button>
            <button
              onClick={() => {
                setShowNewScan(false);
                alert('Scan launched!');
              }}
              className="flex-1 rounded bg-purple-600 px-4 py-2 text-sm font-medium text-white hover:bg-purple-700"
            >
              Launch Scan
            </button>
          </div>
        }
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm text-slate-300 mb-1">Scan Name</label>
            <input type="text" placeholder="e.g., Nuclei - Web Scan" className="w-full rounded bg-slate-800 border border-slate-700 px-3 py-2 text-sm text-slate-50" />
          </div>
          <div>
            <label className="block text-sm text-slate-300 mb-1">Plugin</label>
            <select className="w-full rounded bg-slate-800 border border-slate-700 px-3 py-2 text-sm text-slate-50">
              <option>Nmap</option>
              <option>Nuclei</option>
              <option>HTTPX</option>
              <option>Katana</option>
              <option>Subfinder</option>
            </select>
          </div>
          <div>
            <label className="block text-sm text-slate-300 mb-1">Target</label>
            <input type="text" placeholder="e.g., acme.com" className="w-full rounded bg-slate-800 border border-slate-700 px-3 py-2 text-sm text-slate-50" />
          </div>
          <div>
            <label className="block text-sm text-slate-300 mb-1">Priority</label>
            <select className="w-full rounded bg-slate-800 border border-slate-700 px-3 py-2 text-sm text-slate-50">
              <option>Medium (50)</option>
              <option>High (75)</option>
              <option>Critical (100)</option>
            </select>
          </div>
        </div>
      </Modal>
    </MainLayout>
  );
}
