import React, { useState, useEffect } from 'react';
import { X, CheckCircle2, UserCheck, Calendar, Tag, Sparkles, Quote, Bot, Save, AlertTriangle } from 'lucide-react';

export default function TaskDetailDrawer({ item, onClose, onUpdateItem, onMarkComplete }) {
  if (!item) return null;

  const [title, setTitle] = useState(item.task_title || '');
  const [desc, setDesc] = useState(item.task_description || '');
  const [owner, setOwner] = useState(item.owner || 'Unassigned');
  const [deadline, setDeadline] = useState(item.deadline || '');
  const [priority, setPriority] = useState(item.priority || 'medium');

  useEffect(() => {
    setTitle(item.task_title || '');
    setDesc(item.task_description || '');
    setOwner(item.owner || 'Unassigned');
    setDeadline(item.deadline || '');
    setPriority(item.priority || 'medium');
  }, [item]);

  const ownerOptions = ['Riya', 'David', 'Sarah', 'Alex', 'Vikram', 'Priya', 'Marcus', 'Samantha', 'Jessica', 'Unassigned'];

  const handleSave = () => {
    onUpdateItem(item.id, {
      task_title: title,
      task_description: desc,
      owner,
      deadline: deadline || null,
      priority
    });
  };

  const confidencePercent = Math.round((item.confidence || 0.90) * 100);

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-slate-900/30 backdrop-blur-xs flex justify-end">
      <div className="w-full max-w-lg bg-white h-full shadow-2xl border-l border-slate-200 flex flex-col animate-slide-in-right">
        
        {/* Drawer Header */}
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-lg bg-indigo-50 text-indigo-600 border border-indigo-100">
              <Bot className="w-4 h-4" />
            </span>
            <span className="text-xs font-bold uppercase tracking-wider text-slate-700">Task Details & AI Evidence</span>
          </div>
          <button 
            onClick={onClose}
            className="p-1 rounded-md text-slate-400 hover:text-slate-700 hover:bg-slate-200 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Drawer Scrollable Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          
          {/* Title & Description Editor */}
          <div className="space-y-3">
            <div>
              <label className="block text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-1">Task Title</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full text-base font-bold text-slate-900 bg-slate-50 p-2.5 rounded-lg border border-slate-200 focus:border-indigo-500 focus:bg-white outline-none"
              />
            </div>

            <div>
              <label className="block text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-1">Task Description</label>
              <textarea
                value={desc}
                onChange={(e) => setDesc(e.target.value)}
                rows={3}
                className="w-full text-xs text-slate-700 bg-slate-50 p-2.5 rounded-lg border border-slate-200 focus:border-indigo-500 focus:bg-white outline-none"
              />
            </div>
          </div>

          {/* Key Attributes Grid */}
          <div className="grid grid-cols-2 gap-4 p-4 rounded-xl bg-slate-50 border border-slate-200">
            {/* Owner Reassignment Dropdown */}
            <div>
              <label className="block text-[11px] font-semibold text-slate-500 mb-1 flex items-center gap-1">
                <UserCheck className="w-3.5 h-3.5 text-indigo-600" />
                <span>Owner</span>
              </label>
              <select
                value={owner}
                onChange={(e) => setOwner(e.target.value)}
                className="w-full bg-white text-xs font-semibold text-slate-800 p-2 rounded-md border border-slate-200 focus:border-indigo-500 outline-none"
              >
                {ownerOptions.map(o => (
                  <option key={o} value={o}>{o}</option>
                ))}
              </select>
            </div>

            {/* Deadline */}
            <div>
              <label className="block text-[11px] font-semibold text-slate-500 mb-1 flex items-center gap-1">
                <Calendar className="w-3.5 h-3.5 text-indigo-600" />
                <span>Deadline</span>
              </label>
              <input
                type="text"
                value={deadline}
                onChange={(e) => setDeadline(e.target.value)}
                placeholder="e.g. 2026-07-28"
                className="w-full bg-white text-xs text-slate-800 p-2 rounded-md border border-slate-200 focus:border-indigo-500 outline-none"
              />
            </div>

            {/* Priority */}
            <div>
              <label className="block text-[11px] font-semibold text-slate-500 mb-1 flex items-center gap-1">
                <Tag className="w-3.5 h-3.5 text-indigo-600" />
                <span>Priority</span>
              </label>
              <select
                value={priority}
                onChange={(e) => setPriority(e.target.value)}
                className="w-full bg-white text-xs font-semibold text-slate-800 p-2 rounded-md border border-slate-200 focus:border-indigo-500 outline-none"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </div>

            {/* Status */}
            <div>
              <label className="block text-[11px] font-semibold text-slate-500 mb-1">Status</label>
              <span className="inline-block text-xs font-semibold px-2.5 py-1.5 rounded-md bg-white border border-slate-200 text-slate-800 uppercase tracking-wide">
                {item.status}
              </span>
            </div>
          </div>

          {/* AI Confidence Meter */}
          <div className="p-4 rounded-xl bg-violet-50/50 border border-violet-100">
            <div className="flex items-center justify-between text-xs font-semibold text-violet-900 mb-1.5">
              <span className="flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-violet-600" />
                <span>AI Confidence Score</span>
              </span>
              <span className="font-mono text-violet-700">{confidencePercent}%</span>
            </div>
            <div className="w-full bg-violet-200/60 rounded-full h-2 overflow-hidden">
              <div 
                className="bg-violet-600 h-2 rounded-full transition-all duration-500" 
                style={{ width: `${confidencePercent}%` }}
              />
            </div>
            <p className="text-[11px] text-violet-700 mt-1">
              {confidencePercent >= 90 ? 'High confidence extraction' : confidencePercent >= 70 ? 'Medium confidence' : 'Low confidence — Requires user review'}
            </p>
          </div>

          {/* SOURCE EVIDENCE / EXPLAINABLE AI */}
          <div className="space-y-2">
            <div className="flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-slate-700">
              <Quote className="w-4 h-4 text-indigo-600" />
              <span>Source Evidence (Transcript Quote)</span>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-900 text-slate-200 text-xs font-mono border border-slate-800 leading-relaxed">
              "{item.source_quote || 'Verbatim transcript quote extracted by LLM worker.'}"
            </div>
          </div>

          {/* AGENT DECISION REASONING SIGNALS */}
          <div className="p-4 rounded-xl bg-indigo-50/50 border border-indigo-100 space-y-2">
            <h4 className="text-xs font-bold uppercase tracking-wider text-indigo-900 flex items-center gap-1.5">
              <Bot className="w-4 h-4 text-indigo-600" />
              <span>Agent Decision Signals</span>
            </h4>
            <div className="text-xs text-indigo-900 space-y-1">
              <p><strong>Action:</strong> {item.status === 'reminded' ? 'SEND_REMINDER' : item.status === 'completed' ? 'STOP_REMINDERS' : 'MONITOR'}</p>
              <p><strong>Reason:</strong> {item.status === 'completed' ? 'Task marked completed by user.' : `Automated loop monitoring task state for @${item.owner}.`}</p>
              <p><strong>Attempt Counter:</strong> #{item.reminders_sent} / 3</p>
              <p><strong>Next Evaluation:</strong> 30 seconds</p>
            </div>
          </div>

        </div>

        {/* Drawer Footer Actions */}
        <div className="p-4 border-t border-slate-200 bg-slate-50 flex items-center justify-between gap-3">
          <button
            onClick={handleSave}
            className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold shadow-xs transition"
          >
            <Save className="w-4 h-4" />
            <span>Save Changes</span>
          </button>

          {item.status !== 'completed' && (
            <button
              onClick={() => {
                onMarkComplete(item.id);
                onClose();
              }}
              className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold shadow-xs transition"
            >
              <CheckCircle2 className="w-4 h-4" />
              <span>Mark Complete</span>
            </button>
          )}
        </div>

      </div>
    </div>
  );
}
