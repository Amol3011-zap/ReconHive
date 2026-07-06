"use client";

import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen bg-slate-900 text-slate-50">
      <nav className="border-b border-slate-700 bg-slate-950 p-4">
        <h1 className="text-2xl font-bold">ReconHive</h1>
      </nav>
      <main className="max-w-6xl mx-auto p-8">
        <h2 className="text-3xl font-bold mb-8">Enterprise Security Assessment Platform</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Link href="/engagements" className="bg-slate-800 p-6 rounded hover:bg-slate-700">
            <div className="text-lg font-bold">Engagements</div>
            <div className="text-sm text-slate-400">Manage assessments</div>
          </Link>
          <Link href="/assets" className="bg-slate-800 p-6 rounded hover:bg-slate-700">
            <div className="text-lg font-bold">Assets</div>
            <div className="text-sm text-slate-400">Inventory</div>
          </Link>
          <Link href="/targets" className="bg-slate-800 p-6 rounded hover:bg-slate-700">
            <div className="text-lg font-bold">Targets</div>
            <div className="text-sm text-slate-400">Scope</div>
          </Link>
          <Link href="/scans" className="bg-slate-800 p-6 rounded hover:bg-slate-700">
            <div className="text-lg font-bold">Scans</div>
            <div className="text-sm text-slate-400">Execution</div>
          </Link>
        </div>
      </main>
    </div>
  );
}
