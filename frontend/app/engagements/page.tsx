"use client";

import Link from "next/link";

export default function EngagementsPage() {
  return (
    <div className="min-h-screen bg-slate-900 text-slate-50">
      <nav className="border-b border-slate-700 bg-slate-950 p-4 flex justify-between">
        <h1 className="text-2xl font-bold">ReconHive</h1>
        <Link href="/" className="text-cyan-400">Dashboard</Link>
      </nav>
      <main className="max-w-6xl mx-auto p-8">
        <h2 className="text-3xl font-bold mb-8">Engagements</h2>
        <div className="bg-slate-800 p-6 rounded border border-slate-700">
          <p className="text-slate-300">Manage your security assessments and engagements</p>
        </div>
      </main>
    </div>
  );
}
