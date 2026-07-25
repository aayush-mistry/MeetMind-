import React from 'react';
import { Bot, Wifi, WifiOff, Sparkles, RefreshCw, LayoutDashboard, FolderKanban, Activity, Settings } from 'lucide-react';

export default function Header({ 
  wsConnected, 
  activeTab, 
  setActiveTab, 
  onResetMeeting, 
  onOpenMeetings 
}) {
  return (
    <header className="sticky top-0 z-30 bg-white border-b border-slate-200 px-6 py-3.5 shadow-sm">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        
        {/* Left: Logo & Brand & Nav Tabs */}
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-indigo-600 text-white shadow-md shadow-indigo-500/20">
              <Bot className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-slate-900 tracking-tight text-base">AI Meeting Agent</span>
                <span className="px-2 py-0.5 text-[11px] font-semibold rounded-md bg-indigo-50 text-indigo-700 border border-indigo-200/60">
                  Agentic AI
                </span>
              </div>
            </div>
          </div>

          {/* Navigation View Switcher */}
          <nav className="hidden sm:flex items-center gap-1 bg-slate-100/80 p-1 rounded-lg border border-slate-200/80">
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition ${
                activeTab === 'dashboard'
                  ? 'bg-white text-slate-900 shadow-sm border border-slate-200'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <LayoutDashboard className="w-3.5 h-3.5" />
              <span>Dashboard</span>
            </button>
            
            <button
              onClick={onOpenMeetings}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition text-slate-600 hover:text-slate-900`}
            >
              <FolderKanban className="w-3.5 h-3.5" />
              <span>Meetings</span>
            </button>
          </nav>
        </div>

        {/* Right: Live Connection Status & Actions */}
        <div className="flex items-center gap-3">
          
          {/* WebSocket Status Indicator */}
          <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium border transition-colors ${
            wsConnected 
              ? 'bg-emerald-50 text-emerald-700 border-emerald-200' 
              : 'bg-rose-50 text-rose-700 border-rose-200'
          }`}>
            {wsConnected ? (
              <>
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                <span>Live Connected</span>
              </>
            ) : (
              <>
                <span className="w-2 h-2 rounded-full bg-rose-500"></span>
                <span>Reconnecting...</span>
              </>
            )}
          </div>

          {/* Reset Demo Button */}
          <button
            onClick={onResetMeeting}
            title="Reset Demo"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-medium transition border border-slate-200 active:scale-95"
          >
            <RefreshCw className="w-3.5 h-3.5 text-slate-500" />
            <span>Reset Demo</span>
          </button>
        </div>

      </div>
    </header>
  );
}
