import React from 'react';
import { Plus, Zap, Sparkles } from 'lucide-react';

export default function DashboardHero({ onNewMeetingClick }) {
  return (
    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 py-2 border-b border-slate-200/80 pb-4">
      <div>
        <div className="flex items-center gap-2">
          <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
            Meeting Intelligence Dashboard
          </h1>
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200">
            <Zap className="w-3 h-3 text-amber-500 fill-amber-500" />
            <span>Demo Time Acceleration Active</span>
          </span>
        </div>
        <p className="text-xs sm:text-sm text-slate-500 mt-1">
          Turn meeting conversations into structured commitments, decisions, and autonomous follow-ups.
        </p>
      </div>

      <div className="flex items-center gap-2 shrink-0">
        <button
          onClick={onNewMeetingClick}
          className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold shadow-sm transition active:scale-95"
        >
          <Plus className="w-4 h-4" />
          <span>New Meeting</span>
        </button>
      </div>
    </div>
  );
}
