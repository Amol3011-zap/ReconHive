import React from 'react';

interface MetricCardProps {
  label: string;
  value: string | number;
  trend?: { direction: 'up' | 'down'; percent: number };
  icon?: React.ReactNode;
  color?: 'blue' | 'purple' | 'green' | 'red' | 'amber' | 'cyan';
}

const colorMap = {
  blue: 'bg-blue-950 border-blue-700 text-blue-300',
  purple: 'bg-purple-950 border-purple-700 text-purple-300',
  green: 'bg-green-950 border-green-700 text-green-300',
  red: 'bg-red-950 border-red-700 text-red-300',
  amber: 'bg-amber-950 border-amber-700 text-amber-300',
  cyan: 'bg-cyan-950 border-cyan-700 text-cyan-300',
};

export function MetricCard({
  label,
  value,
  trend,
  icon,
  color = 'blue',
}: MetricCardProps) {
  return (
    <div className={`rounded-lg border p-6 backdrop-blur-sm ${colorMap[color]}`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-slate-300">{label}</p>
          <p className="mt-2 text-3xl font-bold text-slate-50">{value}</p>
          {trend && (
            <p className={`mt-2 text-sm ${trend.direction === 'up' ? 'text-green-400' : 'text-red-400'}`}>
              {trend.direction === 'up' ? '↑' : '↓'} {trend.percent}% from last month
            </p>
          )}
        </div>
        {icon && <div className="text-3xl opacity-50">{icon}</div>}
      </div>
    </div>
  );
}
