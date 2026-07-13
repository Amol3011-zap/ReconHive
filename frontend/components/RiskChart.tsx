'use client';

import React from 'react';

interface RiskData {
  CRITICAL: number;
  HIGH: number;
  MEDIUM: number;
  LOW: number;
  INFO: number;
}

export function RiskChart({ data }: { data: RiskData }) {
  const total = Object.values(data).reduce((a, b) => a + b, 0);

  const severities = [
    { label: 'Critical', value: data.CRITICAL, color: 'bg-red-600', colorLight: 'text-red-400' },
    { label: 'High', value: data.HIGH, color: 'bg-orange-600', colorLight: 'text-orange-400' },
    { label: 'Medium', value: data.MEDIUM, color: 'bg-yellow-600', colorLight: 'text-yellow-400' },
    { label: 'Low', value: data.LOW, color: 'bg-blue-600', colorLight: 'text-blue-400' },
    { label: 'Info', value: data.INFO, color: 'bg-slate-600', colorLight: 'text-slate-400' },
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-end justify-center gap-1" style={{ height: '200px' }}>
        {severities.map((severity) => {
          const percent = total > 0 ? (severity.value / total) * 100 : 0;
          return (
            <div
              key={severity.label}
              className={`${severity.color} rounded-t transition-all hover:opacity-80`}
              style={{
                width: `${100 / severities.length}%`,
                height: `${Math.max(5, percent * 2)}px`,
              }}
              title={`${severity.label}: ${severity.value}`}
            />
          );
        })}
      </div>

      <div className="grid grid-cols-2 gap-2">
        {severities.map((severity) => (
          <div key={severity.label} className="flex items-center gap-2">
            <div className={`h-3 w-3 rounded ${severity.color}`} />
            <div>
              <p className="text-xs text-slate-400">{severity.label}</p>
              <p className={`text-sm font-bold ${severity.colorLight}`}>{severity.value}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="rounded-lg bg-slate-900 p-3 text-center">
        <p className="text-2xl font-bold text-slate-50">{total}</p>
        <p className="text-xs text-slate-400">Total Findings</p>
      </div>
    </div>
  );
}
