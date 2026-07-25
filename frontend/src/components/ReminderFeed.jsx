import React, { useState } from 'react';
import { Radio, Pause, Play, Trash2, Clock, AlertTriangle, Bell, Bot, ShieldAlert } from 'lucide-react';

export default function ReminderFeed({ events = [] }) {
  const [isPaused, setIsPaused] = useState(false);
  const [cleared, setCleared] = useState(false);

  const activeEvents = cleared ? [] : events;

  return (
    <div className="saas-card rounded-xl border border-slate-200 p-5 shadow-sm flex flex-col h-full bg-white">
      
      {/* Header & Controls */}
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-200">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-indigo-50 text-indigo-600 border border-indigo-100">
            <Radio className="w-4 h-4 animate-pulse" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-slate-900">Agent Activity Timeline</h2>
            <p className="text-xs text-slate-500">Autonomous reasoning & event log</p>
          </div>
        </div>

        <div className="flex items-center gap-1">
          <button
            onClick={() => setIsPaused(!isPaused)}
            title={isPaused ? 'Resume live feed' : 'Pause live feed'}
            className="p-1.5 rounded-md bg-slate-100 hover:bg-slate-200 text-slate-600 transition text-xs"
          >
            {isPaused ? <Play className="w-3.5 h-3.5" /> : <Pause className="w-3.5 h-3.5" />}
          </button>
          <button
            onClick={() => setCleared(true)}
            title="Clear timeline"
            className="p-1.5 rounded-md bg-slate-100 hover:bg-slate-200 text-slate-600 transition text-xs"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Feed List */}
      <div className="space-y-3 overflow-y-auto max-h-[500px] pr-1 flex-1">
        {activeEvents.length === 0 ? (
          <div className="text-center py-10 px-4 text-slate-400 text-xs">
            <Bot className="w-8 h-8 text-slate-300 mx-auto mb-2 opacity-60" />
            <p className="font-semibold text-slate-600">No agent actions recorded yet</p>
            <p className="text-[11px] text-slate-400 mt-0.5">
              The autonomous decision engine evaluates pending tasks every 20 seconds.
            </p>
          </div>
        ) : (
          activeEvents.map((evt, idx) => {
            const isEscalation = evt.type === 'item_escalated';
            const isRisk = evt.type === 'dependency_at_risk';
            
            return (
              <div 
                key={evt.id || idx}
                className={`p-3.5 rounded-xl border transition-all duration-300 animate-slide-up ${
                  isEscalation
                    ? 'bg-rose-50/60 border-rose-200'
                    : isRisk
                    ? 'bg-amber-50/60 border-amber-200'
                    : 'bg-slate-50 border-slate-200 hover:border-indigo-200'
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <span className={`text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded ${
                    isEscalation
                      ? 'bg-rose-100 text-rose-800'
                      : isRisk
                      ? 'bg-amber-100 text-amber-800'
                      : 'bg-indigo-100 text-indigo-800'
                  }`}>
                    {evt.action || evt.type}
                  </span>

                  <span className="text-[10px] font-mono text-slate-400 flex items-center gap-1">
                    <Clock className="w-3 h-3 text-slate-400" />
                    {new Date(evt.timestamp || Date.now()).toLocaleTimeString()}
                  </span>
                </div>

                <p className="text-xs font-semibold text-slate-900 mt-2">
                  {evt.reason || 'Agent evaluated task state.'}
                </p>

                {evt.target && (
                  <p className="text-xs font-mono text-indigo-700 font-medium mt-1">
                    Target: {evt.target}
                  </p>
                )}

                {evt.signals && evt.signals.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-slate-200/60 text-[11px] text-slate-500 space-y-0.5">
                    <span className="font-semibold text-slate-600 block">Signals:</span>
                    {evt.signals.map((sig, i) => (
                      <div key={i} className="flex items-center gap-1 font-mono text-[10px]">
                        <span className="w-1 h-1 rounded-full bg-indigo-500"></span>
                        <span>{sig}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>

    </div>
  );
}
