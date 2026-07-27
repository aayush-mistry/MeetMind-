import React, { useState } from 'react';
import { useMeeting } from '../context/MeetingContext';
import MeetingSummaryCard from '../components/MeetingSummaryCard';
import ActionItemsTable from '../components/ActionItemsTable';
import ReminderFeed from '../components/ReminderFeed';
import TaskDetailDrawer from '../components/TaskDetailDrawer';
import SpeakersList from '../components/SpeakersList';

const API_BASE = '/api';

export default function LiveMeeting() {
  const {
    meetingId,
    summary,
    items,
    decisions,
    risksBlockers,
    agentEvents,
    isExtracting,
    analysisStageIndex,
    wsConnected,
    setIsExtracting,
    setAnalysisStageIndex
  } = useMeeting();

  const [selectedTask, setSelectedTask] = useState(null);

  const handleSubmitTranscript = async (text) => {
    setIsExtracting(true);
    setAnalysisStageIndex(0);
    try {
      const res = await fetch(`${API_BASE}/transcript/${meetingId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      });
      if (!res.ok) throw new Error(await res.text());
    } catch (err) {
      console.error('Submit transcript error:', err);
      alert(`Failed to process transcript: ${err.message}`);
      setIsExtracting(false);
    }
  };

  const handleMarkComplete = async (itemId) => {
    try { await fetch(`${API_BASE}/meeting/${meetingId}/items/${itemId}/complete`, { method: 'POST' }); } catch (err) {}
  };

  const handleConfirmItem = async (itemId) => {
    try { await fetch(`${API_BASE}/meeting/${meetingId}/items/${itemId}/confirm`, { method: 'POST' }); } catch (err) {}
  };

  const handleUpdateItem = async (itemId, updates) => {
    try {
      await fetch(`${API_BASE}/meeting/${meetingId}/items/${itemId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates)
      });
    } catch (err) {}
  };

  const handleAddManualItem = async (newItemData) => {
    try {
      await fetch(`${API_BASE}/meeting/${meetingId}/items`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newItemData)
      });
    } catch (err) {}
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-800">Live Meeting: <span className="text-indigo-600">{meetingId}</span></h1>
        <div className="flex items-center gap-2 text-sm font-medium">
          <div className={`w-2.5 h-2.5 rounded-full ${wsConnected ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'}`}></div>
          <span className={wsConnected ? 'text-emerald-600' : 'text-red-500'}>
            {wsConnected ? 'Connected to Agent' : 'Disconnected'}
          </span>
        </div>
      </div>

      {summary && <MeetingSummaryCard summary={summary} />}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <ActionItemsTable
            items={items}
            decisions={decisions}
            risksBlockers={risksBlockers}
            onSelectItem={(item) => setSelectedTask(item)}
            onMarkComplete={handleMarkComplete}
            onConfirmItem={handleConfirmItem}
            onAddManualItem={handleAddManualItem}
          />
        </div>
        <div className="lg:col-span-1 space-y-6">
          <ReminderFeed events={agentEvents} />
          {meetingId && <SpeakersList meetingId={meetingId} />}
        </div>
      </div>

      <TaskDetailDrawer
        item={selectedTask}
        onClose={() => setSelectedTask(null)}
        onUpdateItem={handleUpdateItem}
        onMarkComplete={handleMarkComplete}
      />
    </div>
  );
}
