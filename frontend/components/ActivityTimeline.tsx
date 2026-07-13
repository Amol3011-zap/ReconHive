'use client';

import React from 'react';

interface Activity {
  id: string;
  type: 'engagement_created' | 'scan_started' | 'scan_completed' | 'finding_created' | 'evidence_uploaded' | 'job_completed';
  title: string;
  description?: string;
  timestamp: Date;
}

const activityIcons = {
  engagement_created: '📋',
  scan_started: '🚀',
  scan_completed: '✅',
  finding_created: '🚨',
  evidence_uploaded: '📸',
  job_completed: '✔️',
};

const activityColors = {
  engagement_created: 'bg-blue-900/30 border-blue-700',
  scan_started: 'bg-yellow-900/30 border-yellow-700',
  scan_completed: 'bg-green-900/30 border-green-700',
  finding_created: 'bg-red-900/30 border-red-700',
  evidence_uploaded: 'bg-purple-900/30 border-purple-700',
  job_completed: 'bg-cyan-900/30 border-cyan-700',
};

export function ActivityTimeline({ activities }: { activities: Activity[] }) {
  return (
    <div className="space-y-3">
      {activities.slice(0, 6).map((activity, idx) => (
        <div
          key={activity.id}
          className={`flex items-start gap-4 rounded-lg border p-3 ${
            activityColors[activity.type]
          }`}
        >
          <div className="flex-shrink-0 text-lg">
            {activityIcons[activity.type]}
          </div>
          <div className="min-w-0 flex-1">
            <p className="text-sm font-medium text-slate-100">{activity.title}</p>
            {activity.description && (
              <p className="mt-1 text-xs text-slate-400">{activity.description}</p>
            )}
            <p className="mt-1 text-xs text-slate-500">
              {formatTime(activity.timestamp)}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}

function formatTime(date: Date): string {
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);

  if (minutes < 1) return 'just now';
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  if (days < 30) return `${days}d ago`;
  return date.toLocaleDateString();
}
