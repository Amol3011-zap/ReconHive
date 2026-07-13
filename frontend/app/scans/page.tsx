'use client';

import React, { useState } from 'react';
import { MainLayout } from '@/components/MainLayout';
import { Table } from '@/components/Table';
import { Modal } from '@/components/Modal';

export default function ScansPage() {
  const [showNewScan, setShowNewScan] = useState(false);
  const [selectedScan, setSelectedScan] = useState<string | null>(null);

  const [scans] = useState([
    {
      id: '1',
      name: 'Nuclei - Web Scan',
      plugin: 'Nuclei',
      target: 'app.acme.com',
      status: 'Running',
      progress: 79,
      started: '2026-07-13 10:00',
      duration: '01:42:30',
      worker: 'worker-2',
      stages: ['Initialize', '✓ Target validation', '✓ Template loading', '→ Scanning', 'Reporting'],
      logs: [
        '[10:00] Scan started',
        '[10:05] Loaded 500 templates',
        '[10:12] Found 12 vulnerabilities',
        '[10:34] Database updated',
        '[11:42] Scan 79% complete',
      ]
    },
    {
      id: '2',
      name: 'Subdomain Discovery',
      plugin: 'Subfinder',
      target: 'acme.com',
      status: 'Running',
      progress: 45,
      started: '2026-07-13 09:52',
      duration: '01:34:22',
      worker: 'worker-1',
      stages: ['Initialize', '✓ DNS queries', '→ Enumeration', 'Filtering', 'Reporting'],
      logs: [
        '[09:52] Starting subdomain enumeration',
        '[10:01] Found 45 subdomains',
        '[10:15] Filtering duplicates',
        '[11:26] 45% complete',
      ]
    },
    {
      id: '3',
      name: 'Nmap - Full Scan',
      plugin: 'Nmap',
      target: 'acme.com',
      status: 'Running',
      progress: 30,
      started: '2026-07-13 09:47',
      duration: '01:39:45',
      worker: 'worker-3',
      stages: ['Initialize', '✓ Host discovery', '→ Port scanning', 'Service detection', 'Reporting'],
      logs: [
        '[09:47] Port scan started',
        '[10:02] Discovered 150 hosts',
        '[11:27] 30% complete',
      ]
    },
    {
      id: '4',
      name: 'DNS Enumeration',
      plugin: 'dig',
      target: 'acme.com',
      status: 'Completed',
      progress: 100,
      started: '2026-07-13 08:00',
      duration: '00:45:32',
      worker: 'worker-1',
      stages: ['✓ Initialize', '✓ DNS queries', '✓ Results', '✓ Reporting'],
      logs: [
        '[08:00] DNS enumeration started',
        '[08:15] Completed',
        '[08:45] Report generated',
      ]
    },
    {
      id: '5',
      name: 'SSL/TLS Assessment',
      plugin: 'testssl.sh',
      target: 'paymentapp.acme.com',
      status: 'Completed',
      progress: 100,
      started: '2026-07-13 07:30',
      duration: '00:30:15',
      worker: 'worker-2',
      stages: ['✓ Initialize', '✓ Scan', '✓ Analysis', '✓ Reporting'],
      logs: [
        '[07:30] SSL/TLS scan started',
        '[07:35] Detected TLS 1.2',
        '[07:50] Found weak cipher suites',
        '[08:00] Report complete',
      ]
    },
  ]);

  const currentScan = scans.find(s => s.id === selectedScan);

  return (
    <MainLayout title="Scans" subtitle="Monitor and manage security scans">
      <div className="mb-6 flex items-center justify-between">
        <select className="rounded-lg border border-slate-700 bg-slate-900 px-4 py-2 text-slate-50 focus:outline-none focus:ring-2 focus:ring-purple-600">
          <option>All Status</option>
          <option>Running</option>
          <option>Completed</option>
          <option>Failed</option>
        </select>
        <button
          onClick={() => setShowNewScan(true)}
          className="rounded-lg bg-purple-600 px-6 py-2 font-medium text-white hover:bg-purple-700">
          🚀 Launch Scan
        </button>
      </div>

      <div className="rounded-lg border border-slate-700 bg-slate-950 overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-slate-700 bg-slate-900">
              <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">Scan Name</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">Plugin</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">Target</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">Status</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">Progress</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">Duration</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">Worker</th>
            </tr>
          </thead>
          <tbody>
            {scans.map((scan) => (
              <tr
                key={scan.id}
                className="border-b border-slate-800 hover:bg-slate-900/50 transition-colors cursor-pointer"
                onClick={() => setSelectedScan(scan.id)}
              >
                <td className="px-6 py-3 text-sm text-slate-300 font-medium">{scan.name}</td>
                <td className="px-6 py-3 text-sm text-slate-300">{scan.plugin}</td>
                <td className="px-6 py-3 text-sm text-slate-300">{scan.target}</td>
                <td className="px-6 py-3 text-sm">
                  <span className={`inline-block rounded px-2 py-1 text-xs font-semibold ${scan.status === 'Running' ? 'bg-yellow-900/30 text-yellow-300' : 'bg-green-900/30 text-green-300'}`}>{scan.status}</span>
                </td>
                <td className="px-6 py-3 text-sm">
                  <div className="flex items-center gap-2">
                    <div className="h-1.5 w-16 rounded-full bg-slate-700">
                      <div className="h-full rounded-full bg-purple-500" style={{ width: `${scan.progress}%` }} />
                    </div>
                    <span className="text-xs text-slate-400">{scan.progress}%</span>
                  </div>
                </td>
                <td className="px-6 py-3 text-sm text-slate-300">{scan.duration}</td>
                <td className="px-6 py-3 text-sm text-slate-300">{scan.worker}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Scan Details Modal */}
      {currentScan && (
        <Modal
          isOpen={!!selectedScan}
          onClose={() => setSelectedScan(null)}
          title={`${currentScan.name} - Details`}
        >
          <div className="space-y-4">
            {/* Stages */}
            <div>
              <h4 className="text-sm font-semibold text-slate-50 mb-2">Scan Stages</h4>
              <div className="flex items-center justify-between text-xs">
                {currentScan.stages.map((stage, idx) => (
                  <div key={idx} className="text-center">
                    <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold mx-auto mb-1 ${
                      stage.startsWith('✓') ? 'bg-green-600 text-white' :
                      stage.startsWith('→') ? 'bg-yellow-600 text-white' :
                      'bg-slate-700 text-slate-300'
                    }`}>
                      {stage.startsWith('✓') ? '✓' : stage.startsWith('→') ? '●' : idx + 1}
                    </div>
                    <span className="text-slate-400 max-w-16 truncate">{stage.replace('✓', '').replace('→', '').trim()}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Logs */}
            <div>
              <h4 className="text-sm font-semibold text-slate-50 mb-2">Scan Logs</h4>
              <div className="bg-slate-900 rounded p-3 h-40 overflow-y-auto text-xs font-mono text-slate-300 space-y-1">
                {currentScan.logs.map((log, idx) => (
                  <div key={idx}>{log}</div>
                ))}
              </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-slate-500">Status</p>
                <p className="text-sm font-semibold text-slate-300">{currentScan.status}</p>
              </div>
              <div>
                <p className="text-xs text-slate-500">Progress</p>
                <p className="text-sm font-semibold text-slate-300">{currentScan.progress}%</p>
              </div>
              <div>
                <p className="text-xs text-slate-500">Worker</p>
                <p className="text-sm font-semibold text-slate-300">{currentScan.worker}</p>
              </div>
              <div>
                <p className="text-xs text-slate-500">Duration</p>
                <p className="text-sm font-semibold text-slate-300">{currentScan.duration}</p>
              </div>
            </div>
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
                alert('Scan launched! You would see a new entry in the table.');
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
