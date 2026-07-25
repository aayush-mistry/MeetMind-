import React, { useState } from 'react';
import { 
  CheckCircle2, Clock, Bell, UserCheck, Calendar, AlertTriangle, 
  Plus, Edit2, Check, Search, ShieldCheck, Tag, FileCheck, ShieldAlert,
  HelpCircle, Eye, ArrowRight, AlertCircle, Link2
} from 'lucide-react';

export default function ActionItemsTable({ 
  items = [], 
  decisions = [], 
  risksBlockers = [], 
  onSelectItem, 
  onMarkComplete, 
  onConfirmItem,
  onAddManualItem 
}) {
  const [activeTab, setActiveTab] = useState('action_items'); // action_items, decisions, risks_blockers, needs_review
  const [filterStatus, setFilterStatus] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);

  // Manual Add Form
  const [newTaskTitle, setNewTaskTitle] = useState('');
  const [newTaskDesc, setNewTaskDesc] = useState('');
  const [newOwner, setNewOwner] = useState('');
  const [newDeadline, setNewDeadline] = useState('');
  const [newPriority, setNewPriority] = useState('medium');

  const needsReviewCount = items.filter(i => i.needs_review || i.status === 'needs_review').length;
  const atRiskCount = items.filter(i => i.status === 'at_risk' || i.escalated).length + risksBlockers.length;

  const filteredItems = items.filter(item => {
    if (activeTab === 'needs_review') {
      return item.needs_review || item.status === 'needs_review';
    }
    const matchesStatus = filterStatus === 'all' || item.status === filterStatus;
    const matchesSearch = item.task_title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          item.owner.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesStatus && matchesSearch;
  });

  const handleCreateNewItem = (e) => {
    e.preventDefault();
    if (!newTaskTitle.trim()) return;
    onAddManualItem({
      task_title: newTaskTitle.trim(),
      task_description: newTaskDesc.trim() || "",
      owner: newOwner.trim() || 'Unassigned',
      deadline: newDeadline || null,
      priority: newPriority
    });
    setNewTaskTitle('');
    setNewTaskDesc('');
    setNewOwner('');
    setNewDeadline('');
    setNewPriority('medium');
    setShowAddModal(false);
  };

  const getPriorityBadge = (priority) => {
    switch (priority) {
      case 'critical':
      case 'high':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200">
            <AlertTriangle className="w-3 h-3" />
            <span>High</span>
          </span>
        );
      case 'low':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-600 border border-slate-200">
            <Tag className="w-3 h-3" />
            <span>Low</span>
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-50 text-amber-700 border border-amber-200">
            <Tag className="w-3 h-3" />
            <span>Medium</span>
          </span>
        );
    }
  };

  const getStatusBadge = (status, remindersCount, escalated) => {
    if (escalated || status === 'at_risk') {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-100 text-rose-800 border border-rose-300">
          <AlertCircle className="w-3 h-3" />
          <span>At Risk / Escalated</span>
        </span>
      );
    }

    switch (status) {
      case 'completed':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
            <CheckCircle2 className="w-3 h-3" />
            <span>Completed</span>
          </span>
        );
      case 'reminded':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-cyan-50 text-cyan-800 border border-cyan-200">
            <Bell className="w-3 h-3" />
            <span>Reminded ({remindersCount})</span>
          </span>
        );
      case 'due_soon':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-50 text-amber-700 border border-amber-200">
            <Clock className="w-3 h-3" />
            <span>Due Soon</span>
          </span>
        );
      case 'needs_review':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-violet-50 text-violet-700 border border-violet-200">
            <HelpCircle className="w-3 h-3" />
            <span>Needs Review</span>
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200">
            <Clock className="w-3 h-3 text-slate-500" />
            <span>Pending</span>
          </span>
        );
    }
  };

  const getOwnerInitials = (name) => {
    if (!name || name === 'Unassigned') return 'UN';
    const parts = name.trim().split(' ');
    if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase();
    return name.slice(0, 2).toUpperCase();
  };

  return (
    <div className="saas-card rounded-xl border border-slate-200 p-5 shadow-sm flex flex-col h-full bg-white">
      
      {/* Workspace Main Navigation Tabs */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-5 border-b border-slate-200 pb-3">
        <div className="flex items-center gap-2 overflow-x-auto">
          <button
            onClick={() => setActiveTab('action_items')}
            className={`flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-xs font-semibold transition border ${
              activeTab === 'action_items'
                ? 'bg-slate-900 text-white border-slate-900 shadow-xs'
                : 'text-slate-600 hover:bg-slate-100 border-transparent'
            }`}
          >
            <span>Action Items</span>
            <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-slate-700 text-slate-200 font-mono">
              {items.length}
            </span>
          </button>

          <button
            onClick={() => setActiveTab('decisions')}
            className={`flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-xs font-semibold transition border ${
              activeTab === 'decisions'
                ? 'bg-slate-900 text-white border-slate-900 shadow-xs'
                : 'text-slate-600 hover:bg-slate-100 border-transparent'
            }`}
          >
            <FileCheck className="w-3.5 h-3.5 text-blue-400" />
            <span>Decisions</span>
            <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-slate-700 text-slate-200 font-mono">
              {decisions.length}
            </span>
          </button>

          <button
            onClick={() => setActiveTab('risks_blockers')}
            className={`flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-xs font-semibold transition border ${
              activeTab === 'risks_blockers'
                ? 'bg-slate-900 text-white border-slate-900 shadow-xs'
                : 'text-slate-600 hover:bg-slate-100 border-transparent'
            }`}
          >
            <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
            <span>Risks & Blockers</span>
            {atRiskCount > 0 && (
              <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-amber-500 text-white font-mono">
                {atRiskCount}
              </span>
            )}
          </button>

          <button
            onClick={() => setActiveTab('needs_review')}
            className={`flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-xs font-semibold transition border ${
              activeTab === 'needs_review'
                ? 'bg-slate-900 text-white border-slate-900 shadow-xs'
                : 'text-slate-600 hover:bg-slate-100 border-transparent'
            }`}
          >
            <HelpCircle className="w-3.5 h-3.5 text-violet-400" />
            <span>Needs Review</span>
            {needsReviewCount > 0 && (
              <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-violet-600 text-white font-mono">
                {needsReviewCount}
              </span>
            )}
          </button>
        </div>

        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold shadow-xs transition active:scale-95 shrink-0"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>Add Item</span>
        </button>
      </div>

      {/* Sub-Filter & Search */}
      {activeTab === 'action_items' && (
        <div className="flex flex-col sm:flex-row items-center justify-between gap-3 mb-4 bg-slate-50 p-2 rounded-lg border border-slate-200">
          <div className="flex items-center gap-1 overflow-x-auto w-full sm:w-auto">
            {[
              { id: 'all', label: 'All Items' },
              { id: 'pending', label: 'Pending' },
              { id: 'reminded', label: 'Reminded' },
              { id: 'at_risk', label: 'At Risk' },
              { id: 'completed', label: 'Completed' }
            ].map(f => (
              <button
                key={f.id}
                onClick={() => setFilterStatus(f.id)}
                className={`px-3 py-1 text-xs rounded-md font-medium transition ${
                  filterStatus === f.id
                    ? 'bg-white text-slate-900 shadow-xs border border-slate-200'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                {f.label}
              </button>
            ))}
          </div>

          <div className="relative w-full sm:w-64">
            <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search tasks or owners..."
              className="w-full bg-white text-xs text-slate-800 placeholder-slate-400 rounded-md pl-8 pr-3 py-1.5 border border-slate-200 focus:border-indigo-500 outline-none"
            />
          </div>
        </div>
      )}

      {/* Content Area */}
      <div className="overflow-x-auto flex-1">
        
        {/* TAB 1: ACTION ITEMS & TAB 4: NEEDS REVIEW */}
        {(activeTab === 'action_items' || activeTab === 'needs_review') && (
          filteredItems.length === 0 ? (
            <div className="text-center py-12 px-4 border border-dashed border-slate-200 rounded-xl bg-slate-50/50">
              <ShieldCheck className="w-10 h-10 text-slate-400 mx-auto mb-2" />
              <p className="text-sm font-semibold text-slate-700">No action items found</p>
              <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
                {activeTab === 'needs_review' 
                  ? 'All AI-extracted items have high confidence and assigned owners!' 
                  : 'Submit a meeting transcript above to extract commitments.'}
              </p>
            </div>
          ) : (
            <table className="w-full text-left text-xs text-slate-700">
              <thead className="text-[11px] font-bold uppercase tracking-wider text-slate-500 bg-slate-50 border-b border-slate-200">
                <tr>
                  <th className="py-3 px-4 w-[38%]">Task Title & Description</th>
                  <th className="py-3 px-3 w-[12%]">Owner</th>
                  <th className="py-3 px-3 w-[12%]">Deadline</th>
                  <th className="py-3 px-3 w-[10%]">Priority</th>
                  <th className="py-3 px-3 w-[14%]">Status</th>
                  <th className="py-3 px-3 w-[14%] text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredItems.map((item) => (
                  <tr 
                    key={item.id}
                    onClick={() => onSelectItem(item)}
                    className="hover:bg-indigo-50/30 cursor-pointer transition-colors group"
                  >
                    {/* Task Title & Description */}
                    <td className="py-3.5 px-4">
                      <div className="flex items-start gap-2">
                        <div>
                          <p className={`font-semibold text-slate-900 text-xs sm:text-sm group-hover:text-indigo-600 transition-colors ${
                            item.status === 'completed' ? 'line-through text-slate-400' : ''
                          }`}>
                            {item.task_title}
                          </p>
                          {item.task_description && (
                            <p className="text-[11px] text-slate-500 mt-0.5 line-clamp-1">
                              {item.task_description}
                            </p>
                          )}
                          {item.dependencies && item.dependencies.length > 0 && (
                            <div className="flex items-center gap-1 text-[10px] text-amber-700 font-mono mt-1">
                              <Link2 className="w-3 h-3 text-amber-500" />
                              <span>Depends on: {item.dependencies.join(', ')}</span>
                            </div>
                          )}
                        </div>
                      </div>
                    </td>

                    {/* Owner Avatar & Name */}
                    <td className="py-3.5 px-3 whitespace-nowrap">
                      <div className="flex items-center gap-1.5">
                        <div className={`w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold text-white shrink-0 ${
                          item.owner === 'Unassigned' ? 'bg-slate-400' : 'bg-indigo-600'
                        }`}>
                          {getOwnerInitials(item.owner)}
                        </div>
                        <span className={`font-medium text-xs ${item.owner === 'Unassigned' ? 'text-slate-400 italic' : 'text-slate-800'}`}>
                          {item.owner}
                        </span>
                      </div>
                    </td>

                    {/* Deadline */}
                    <td className="py-3.5 px-3 whitespace-nowrap">
                      <div className="flex items-center gap-1 text-slate-600">
                        <Calendar className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                        <span className="text-xs">{item.deadline || 'No deadline'}</span>
                      </div>
                    </td>

                    {/* Priority */}
                    <td className="py-3.5 px-3 whitespace-nowrap">
                      {getPriorityBadge(item.priority)}
                    </td>

                    {/* Status */}
                    <td className="py-3.5 px-3 whitespace-nowrap">
                      {getStatusBadge(item.status, item.reminders_sent, item.escalated)}
                    </td>

                    {/* Actions */}
                    <td className="py-3.5 px-3 text-right whitespace-nowrap" onClick={(e) => e.stopPropagation()}>
                      <div className="flex items-center justify-end gap-1.5">
                        {item.needs_review && (
                          <button
                            onClick={() => onConfirmItem(item.id)}
                            className="px-2 py-1 rounded bg-violet-50 hover:bg-violet-100 text-violet-700 text-[11px] font-medium border border-violet-200"
                          >
                            Confirm
                          </button>
                        )}
                        {item.status !== 'completed' ? (
                          <button
                            onClick={() => onMarkComplete(item.id)}
                            className="px-2.5 py-1 rounded-md bg-emerald-50 hover:bg-emerald-100 text-emerald-700 text-[11px] font-semibold border border-emerald-200 transition"
                          >
                            Done
                          </button>
                        ) : (
                          <span className="text-[11px] text-emerald-600 font-medium">Done</span>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )
        )}

        {/* TAB 2: DECISIONS */}
        {activeTab === 'decisions' && (
          decisions.length === 0 ? (
            <div className="text-center py-12 px-4 border border-dashed border-slate-200 rounded-xl bg-slate-50">
              <FileCheck className="w-10 h-10 text-slate-400 mx-auto mb-2" />
              <p className="text-sm font-semibold text-slate-700">No explicit decisions detected</p>
              <p className="text-xs text-slate-500 mt-1">Submit a meeting transcript to extract consensus decisions.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {decisions.map((d) => (
                <div key={d.id} className="p-4 rounded-xl border border-blue-100 bg-blue-50/30 hover:bg-blue-50/60 transition">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-blue-100 text-blue-800 border border-blue-200">
                        Decision
                      </span>
                      <h4 className="text-sm font-bold text-slate-900 mt-1">{d.decision}</h4>
                    </div>
                    <span className="text-xs font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200 shrink-0">
                      {Math.round(d.confidence * 100)}% Confidence
                    </span>
                  </div>

                  {d.source_quote && (
                    <p className="text-xs font-mono text-slate-600 mt-2 bg-white/80 p-2 rounded border border-slate-200">
                      "{d.source_quote}"
                    </p>
                  )}

                  <div className="flex items-center gap-2 mt-2 text-[11px] text-slate-500">
                    <span>Decided By: <strong>{d.decided_by}</strong></span>
                  </div>
                </div>
              ))}
            </div>
          )
        )}

        {/* TAB 3: RISKS & BLOCKERS */}
        {activeTab === 'risks_blockers' && (
          risksBlockers.length === 0 ? (
            <div className="text-center py-12 px-4 border border-dashed border-slate-200 rounded-xl bg-slate-50">
              <ShieldCheck className="w-10 h-10 text-slate-400 mx-auto mb-2" />
              <p className="text-sm font-semibold text-slate-700">No significant risks or blockers detected</p>
              <p className="text-xs text-slate-500 mt-1">All discussion items appear clear of major dependency risks!</p>
            </div>
          ) : (
            <div className="space-y-3">
              {risksBlockers.map((rb) => (
                <div 
                  key={rb.id}
                  className={`p-4 rounded-xl border ${
                    rb.type === 'blocker' ? 'border-rose-200 bg-rose-50/40' : 'border-amber-200 bg-amber-50/40'
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-center gap-2">
                      <span className={`text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded border ${
                        rb.type === 'blocker' ? 'bg-rose-100 text-rose-800 border-rose-300' : 'bg-amber-100 text-amber-800 border-amber-300'
                      }`}>
                        {rb.type}
                      </span>
                      <span className="text-xs font-semibold text-slate-600">Severity: {rb.severity.toUpperCase()}</span>
                    </div>
                    <span className="text-xs font-mono text-slate-500">{Math.round(rb.confidence * 100)}% Confidence</span>
                  </div>

                  <h4 className="text-sm font-bold text-slate-900 mt-1.5">{rb.description}</h4>

                  {rb.source_quote && (
                    <p className="text-xs font-mono text-slate-600 mt-2 bg-white/80 p-2 rounded border border-slate-200">
                      "{rb.source_quote}"
                    </p>
                  )}

                  <div className="flex flex-wrap items-center gap-3 mt-2 text-[11px] text-slate-600">
                    {rb.blocked_task && <span>Blocked Task: <strong>{rb.blocked_task}</strong></span>}
                    {rb.depends_on && <span>Depends On: <strong>{rb.depends_on}</strong></span>}
                  </div>
                </div>
              ))}
            </div>
          )
        )}

      </div>

      {/* Manual Add Item Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="saas-card bg-white border border-slate-300 rounded-xl p-6 max-w-md w-full shadow-xl animate-fade-in">
            <h3 className="text-base font-bold text-slate-900 mb-1">Add Action Item</h3>
            <p className="text-xs text-slate-500 mb-4">Manually append an action commitment to this meeting.</p>
            
            <form onSubmit={handleCreateNewItem} className="space-y-3">
              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Task Title</label>
                <input
                  type="text"
                  required
                  value={newTaskTitle}
                  onChange={(e) => setNewTaskTitle(e.target.value)}
                  placeholder="e.g. Finish API rate limiting"
                  className="w-full bg-slate-50 text-xs text-slate-800 rounded-lg p-2.5 border border-slate-200 focus:border-indigo-500 outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Task Description</label>
                <input
                  type="text"
                  value={newTaskDesc}
                  onChange={(e) => setNewTaskDesc(e.target.value)}
                  placeholder="e.g. Complete remaining WebSocket fallback logic"
                  className="w-full bg-slate-50 text-xs text-slate-800 rounded-lg p-2.5 border border-slate-200 focus:border-indigo-500 outline-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-700 mb-1">Owner</label>
                  <input
                    type="text"
                    value={newOwner}
                    onChange={(e) => setNewOwner(e.target.value)}
                    placeholder="e.g. Riya"
                    className="w-full bg-slate-50 text-xs text-slate-800 rounded-lg p-2.5 border border-slate-200 focus:border-indigo-500 outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-700 mb-1">Deadline</label>
                  <input
                    type="text"
                    value={newDeadline}
                    onChange={(e) => setNewDeadline(e.target.value)}
                    placeholder="e.g. 2026-07-28"
                    className="w-full bg-slate-50 text-xs text-slate-800 rounded-lg p-2.5 border border-slate-200 focus:border-indigo-500 outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Priority</label>
                <select
                  value={newPriority}
                  onChange={(e) => setNewPriority(e.target.value)}
                  className="w-full bg-slate-50 text-xs text-slate-800 rounded-lg p-2.5 border border-slate-200 focus:border-indigo-500 outline-none"
                >
                  <option value="low">Low Priority</option>
                  <option value="medium">Medium Priority</option>
                  <option value="high">High Priority</option>
                  <option value="critical">Critical Priority</option>
                </select>
              </div>

              <div className="flex items-center justify-end gap-2 pt-3 border-t border-slate-200">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-3 py-1.5 rounded-md bg-slate-100 text-slate-600 text-xs font-medium hover:bg-slate-200"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 rounded-md bg-indigo-600 text-white text-xs font-semibold hover:bg-indigo-700 shadow-xs"
                >
                  Create Item
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
