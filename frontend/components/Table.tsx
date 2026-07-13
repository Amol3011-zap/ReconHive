'use client';

import React from 'react';

interface Column {
  key: string;
  label: string;
  render?: (value: any, row: any) => React.ReactNode;
  width?: string;
}

interface TableProps {
  columns: Column[];
  data: any[];
  title?: string;
}

export function Table({ columns, data, title }: TableProps) {
  return (
    <div className="overflow-hidden rounded-lg border border-slate-700 bg-slate-950">
      {title && (
        <div className="border-b border-slate-700 px-6 py-4">
          <h3 className="font-semibold text-slate-50">{title}</h3>
        </div>
      )}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-slate-700 bg-slate-900">
              {columns.map((col) => (
                <th
                  key={col.key}
                  className="px-6 py-3 text-left text-sm font-semibold text-slate-300"
                  style={{ width: col.width }}
                >
                  {col.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row, idx) => (
              <tr
                key={idx}
                className="border-b border-slate-800 hover:bg-slate-900/50 transition-colors"
              >
                {columns.map((col) => (
                  <td key={col.key} className="px-6 py-3 text-sm text-slate-300">
                    {col.render ? col.render(row[col.key], row) : row[col.key]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {data.length === 0 && (
        <div className="px-6 py-8 text-center text-slate-400">
          No data available
        </div>
      )}
    </div>
  );
}
