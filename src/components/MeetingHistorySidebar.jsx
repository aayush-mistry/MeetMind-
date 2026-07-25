import React, { useState, useEffect } from 'react';
import { X, FolderKanban, Plus, Clock, FileText, ChevronRight } from 'lucide-react';

export default function MeetingHistorySidebar({ isOpen, onClose, onSelectMeeting, onNewMeeting }) {
  const [meetings, setMeetings] = useState([]);

  useEffect(() => {
    if (isOpen) {
      fetch('http://localhost:8000/api/meetings')
        .then(res => res.json())
        .then(data => {
          if (Array.isArray(data)) setMeetings(data);
        })
        .catch(err => console.log('Meetings fetch error:', err));
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-slate-900/30 backdrop-blur-xs flex justify-start">
      <div className="w-full max-w-sm bg-white h-full shadow-2xl border-r border-slate-200 flex flex-col animate-fade-in">
        
        {/* Header */}
        <div className="p-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
          <div className="flex items-center gap-2">
            <FolderKanban className="w-4 h-4 text-indigo-600" />
            <h3 className="text-sm font-bold text-slate-900">Meeting History</h3>
          </div>
          <button 
            onClick={onClose}
            className="p-1 rounded-md text-slate-400 hover:text-slate-700 hover:bg-slate-200 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* New Meeting Button */}
        <div className="p-4 border-b border-slate-100">
          <button
            onClick={() => {
              onNewMeeting();
              onClose();
            }}
            className="w-full flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold shadow-xs transition"
          >
            <Plus className="w-4 h-4" />
            <span>Start New Meeting Analysis</span>
          </button>
        </div>

        {/* Meetings List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-2">
          {meetings.length === 0 ? (
            <div className="text-center py-10 text-slate-400 text-xs">
              <FileText className="w-8 h-8 text-slate-300 mx-auto mb-2" />
              <p>No saved meetings found.</p>
            </div>
          ) : (
            meetings.map((m) => (
              <div
                key={m.id}
                onClick={() => {
                  onSelectMeeting(m.id);
                  onClose();
                }}
                className="p-3 rounded-xl border border-slate-200 hover:border-indigo-500 hover:bg-indigo-50/40 cursor-pointer transition flex items-center justify-between group"
              >
                <div>
                  <h4 className="text-xs font-bold text-slate-900 group-hover:text-indigo-600 transition">
                    {m.title}
                  </h4>
                  <p className="text-[10px] font-mono text-slate-400 mt-1 flex items-center gap-1">
                    <Clock className="w-3 h-3 text-slate-400" />
                    {new Date(m.created_at).toLocaleDateString()}
                  </p>
                </div>
                <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-indigo-600 transition" />
              </div>
            ))
          )}
        </div>

      </div>
    </div>
  );
}
