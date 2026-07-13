'use client';

import React, { useState } from 'react';

const suggestions = [
  { icon: '📊', text: 'Summarize engagement' },
  { icon: '🎯', text: 'Show highest-risk assets' },
  { icon: '🔴', text: 'List findings by severity' },
  { icon: '📈', text: 'What changed since last assessment?' },
];

export function AICopilot() {
  const [isOpen, setIsOpen] = useState(true);
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<{ role: 'user' | 'assistant'; text: string }[]>([
    {
      role: 'assistant',
      text: 'Hello! I\'m your ReconHive AI Copilot. I can help you analyze findings, summarize assessments, and identify risks. What would you like to know?',
    },
  ]);

  const handleSend = (text: string) => {
    if (!text.trim()) return;

    setMessages((prev) => [...prev, { role: 'user', text }]);
    setInput('');

    // Simulate AI response
    setTimeout(() => {
      const responses: { [key: string]: string } = {
        summarize: 'This engagement includes 4,231 assets across 7 active scans. Critical findings: 9 (Exposed Admin Panel, Missing SPF, Weak TLS). Estimated risk score: 7.8/10.',
        highest: 'Top 5 high-risk assets: 1. app.acme.com (CVSS 9.1), 2. api.acme.com (CVSS 8.9), 3. db.internal (CVSS 8.2), 4. mail.acme.com (CVSS 7.9), 5. vpn.acme.com (CVSS 7.5).',
        findings: 'Critical (9): Exposed Admin Panel, SQL Injection. High (27): Missing SPF, Weak TLS. Medium (48): Default Credentials, Missing Security Headers.',
        changed: 'Since last assessment: 3 new critical findings, 12 findings remediated, 1 new asset added. Overall risk increased by 2%.',
      };

      let response = 'I understand. Can you be more specific about what you\'d like to know?';
      if (text.toLowerCase().includes('summarize')) response = responses.summarize;
      else if (text.toLowerCase().includes('highest') || text.toLowerCase().includes('risk')) response = responses.highest;
      else if (text.toLowerCase().includes('findings') || text.toLowerCase().includes('severity')) response = responses.findings;
      else if (text.toLowerCase().includes('changed') || text.toLowerCase().includes('assessment')) response = responses.changed;

      setMessages((prev) => [...prev, { role: 'assistant', text: response }]);
    }, 800);
  };

  return (
    <div
      className={`fixed bottom-4 right-4 w-96 rounded-lg border border-slate-700 bg-slate-950 shadow-lg transition-all ${
        isOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'
      }`}
    >
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-700 bg-purple-900/30 px-4 py-3">
        <div className="flex items-center gap-2">
          <span className="text-lg">🤖</span>
          <span className="font-semibold text-slate-50">AI Copilot</span>
          <span className="rounded bg-purple-600 px-2 py-0.5 text-xs font-bold text-white">BETA</span>
        </div>
        <button
          onClick={() => setIsOpen(false)}
          className="text-slate-400 hover:text-slate-200"
        >
          ✕
        </button>
      </div>

      {/* Messages */}
      <div className="h-64 space-y-3 overflow-y-auto bg-slate-900/20 p-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex gap-2 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs rounded-lg px-3 py-2 text-sm ${
                msg.role === 'user'
                  ? 'bg-purple-600 text-white'
                  : 'bg-slate-800 text-slate-100'
              }`}
            >
              {msg.text}
            </div>
          </div>
        ))}
      </div>

      {/* Suggestions */}
      {messages.length === 1 && (
        <div className="border-t border-slate-700 px-4 py-3 space-y-2">
          <p className="text-xs text-slate-400">Quick suggestions:</p>
          <div className="space-y-2">
            {suggestions.map((suggestion, idx) => (
              <button
                key={idx}
                onClick={() => handleSend(suggestion.text)}
                className="w-full text-left rounded px-2 py-2 text-xs text-slate-300 hover:bg-slate-800 transition-colors"
              >
                {suggestion.icon} {suggestion.text}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="border-t border-slate-700 p-3">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend(input)}
            placeholder="Ask me anything..."
            className="flex-1 rounded bg-slate-800 px-3 py-2 text-sm text-slate-50 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-600"
          />
          <button
            onClick={() => handleSend(input)}
            className="rounded bg-purple-600 px-3 py-2 text-sm font-medium text-white hover:bg-purple-700 transition-colors"
          >
            ↓
          </button>
        </div>
      </div>
    </div>
  );
}
