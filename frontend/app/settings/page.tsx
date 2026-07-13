'use client';

import React, { useState } from 'react';
import { MainLayout } from '@/components/MainLayout';

export default function SettingsPage() {
  const [settings, setSettings] = useState({
    apiUrl: 'http://localhost:8000/api/v1',
    theme: 'dark',
    notifications: true,
    autoRefresh: true,
  });

  const handleChange = (key: string, value: any) => {
    setSettings((prev) => ({ ...prev, [key]: value }));
  };

  return (
    <MainLayout title="Settings" subtitle="Configure your ReconHive instance">
      <div className="max-w-2xl space-y-6">
        {/* General Settings */}
        <div className="rounded-lg border border-slate-700 bg-slate-950 p-6">
          <h3 className="text-lg font-semibold text-slate-50 mb-4">General Settings</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">API URL</label>
              <input
                type="text"
                value={settings.apiUrl}
                onChange={(e) => handleChange('apiUrl', e.target.value)}
                className="w-full rounded-lg border border-slate-700 bg-slate-900 px-4 py-2 text-slate-50 focus:outline-none focus:ring-2 focus:ring-purple-600"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Theme</label>
              <select
                value={settings.theme}
                onChange={(e) => handleChange('theme', e.target.value)}
                className="w-full rounded-lg border border-slate-700 bg-slate-900 px-4 py-2 text-slate-50 focus:outline-none focus:ring-2 focus:ring-purple-600"
              >
                <option>dark</option>
                <option>light</option>
              </select>
            </div>
          </div>
        </div>

        {/* Preferences */}
        <div className="rounded-lg border border-slate-700 bg-slate-950 p-6">
          <h3 className="text-lg font-semibold text-slate-50 mb-4">Preferences</h3>
          <div className="space-y-4">
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={settings.notifications}
                onChange={(e) => handleChange('notifications', e.target.checked)}
                className="w-4 h-4 rounded"
              />
              <span className="text-sm text-slate-300">Enable notifications</span>
            </label>
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={settings.autoRefresh}
                onChange={(e) => handleChange('autoRefresh', e.target.checked)}
                className="w-4 h-4 rounded"
              />
              <span className="text-sm text-slate-300">Auto-refresh dashboard</span>
            </label>
          </div>
        </div>

        {/* About */}
        <div className="rounded-lg border border-slate-700 bg-slate-950 p-6">
          <h3 className="text-lg font-semibold text-slate-50 mb-4">About</h3>
          <div className="space-y-2 text-sm text-slate-400">
            <p><strong>ReconHive</strong> v0.1-alpha</p>
            <p>Enterprise Security Assessment Management Platform</p>
            <p>© 2026 ReconHive. All rights reserved.</p>
          </div>
        </div>

        {/* Save Button */}
        <button className="rounded-lg bg-purple-600 px-6 py-2 font-medium text-white hover:bg-purple-700">
          💾 Save Settings
        </button>
      </div>
    </MainLayout>
  );
}
