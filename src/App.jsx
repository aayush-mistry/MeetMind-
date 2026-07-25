import React, { useState, useEffect, useRef } from 'react';
import Header from './components/Header';
import DashboardHero from './components/DashboardHero';
import StatsOverview from './components/StatsOverview';
import TranscriptInput from './components/TranscriptInput';
import MeetingSummaryCard from './components/MeetingSummaryCard';
import ActionItemsTable from './components/ActionItemsTable';
import ReminderFeed from './components/ReminderFeed';
import TaskDetailDrawer from './components/TaskDetailDrawer';
import MeetingHistorySidebar from './components/MeetingHistorySidebar';

const BACKEND_HOST = 'localhost:8000';
const API_BASE = `http://${BACKEND_HOST}/api`;
const WS_BASE = `ws://${BACKEND_HOST}/ws`;


export default function App() {
  const [meetingId, setMeetingId] = useState('demo_meeting');
  const [activeNavTab, setActiveNavTab] = useState('dashboard');
  
  // Meeting State
const [uploadFile, setUploadFile] = useState(null);
// Handler to upload recording
const handleUploadRecording = async () => {
  if (!uploadFile) {
    console.warn('No file selected for upload');
    return;
  }
  const form = new FormData();
  form.append('file', uploadFile);
  try {
    const res = await fetch(`${API_BASE}/meeting/upload`, {
      method: 'POST',
      body: form,
    });
    const data = await res.json();
    if (data.meeting_id) {
      setMeetingId(data.meeting_id);
    }
  } catch (err) {
    console.error('Upload error:', err);
  }
};
const [summary, setSummary] = useState(null);
  const [summary, setSummary] = useState(null);
  const [items, setItems] = useState([]);
  const [decisions, setDecisions] = useState([]);
  const [risksBlockers, setRisksBlockers] = useState([]);
  const [agentEvents, setAgentEvents] = useState([]);

  // WebSocket & Pipeline State
  const [wsConnected, setWsConnected] = useState(false);
  const [isExtracting, setIsExtracting] = useState(false);
  const [analysisStageIndex, setAnalysisStageIndex] = useState(-1);

  // UI Drawer & Sidebar State
  const [selectedTask, setSelectedTask] = useState(null);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);

  const wsRef = useRef(null);

  // 1. Load meeting data
  const fetchMeetingData = (mId) => {
    fetch(`${API_BASE}/meeting/${mId}`)
      .then(res => res.json())
      .then(data => {
        if (data.summary) setSummary(data.summary);
        if (Array.isArray(data.action_items)) setItems(data.action_items);
        if (Array.isArray(data.decisions)) setDecisions(data.decisions);
        if (Array.isArray(data.risks_blockers)) setRisksBlockers(data.risks_blockers);
        if (Array.isArray(data.events)) setAgentEvents(data.events);
      })
      .catch(err => console.log('Fetch meeting data error:', err));
  };

  useEffect(() => {
    fetchMeetingData(meetingId);
  }, [meetingId]);

  // 2. WebSocket Real-Time Agentic Pipeline Connection
  useEffect(() => {
    let ws = null;
    let reconnectTimeout = null;

    const connectWebSocket = () => {
      ws = new WebSocket(`${WS_BASE}/meeting/${meetingId}`);
      wsRef.current = ws;

      ws.onopen = () => {
        setWsConnected(true);
        console.log(`[WebSocket] Agent connected to meeting '${meetingId}'`);
      };

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          switch (msg.type) {
            case 'processing_started':
              setIsExtracting(true);
              setAnalysisStageIndex(0);
              break;

            case 'analysis_stage':
              if (typeof msg.stage_index === 'number') {
                setAnalysisStageIndex(msg.stage_index);
              }
              break;

            case 'summary_extracted':
              if (msg.data) setSummary(msg.data);
              break;

            case 'decision_extracted':
              if (msg.data && msg.data.id) {
                setDecisions(prev => [msg.data, ...prev]);
              }
              break;

            case 'risk_extracted':
              if (msg.data && msg.data.id) {
                setRisksBlockers(prev => [msg.data, ...prev]);
              }
              break;

            case 'item_extracted':
              if (msg.data && msg.data.id) {
                setItems(prev => {
                  const exists = prev.some(item => item.id === msg.data.id);
                  if (exists) {
                    return prev.map(item => item.id === msg.data.id ? msg.data : item);
                  }
                  return [...prev, msg.data];
                });
              }
              break;

            case 'processing_complete':
              setIsExtracting(false);
              setAnalysisStageIndex(7);
              break;

            case 'reminder_sent':
              if (msg.data) {
                // Update item status in list
                setItems(prev => prev.map(item => {
                  if (item.id === msg.data.id) {
                    return { 
                      ...item, 
                      status: 'reminded', 
                      reminders_sent: msg.data.reminders_sent 
                    };
                  }
                  return item;
                }));
                // Add event log
                setAgentEvents(prev => [{
                  id: `evt_${Date.now()}`,
                  meeting_id: meetingId,
                  type: 'reminder_sent',
                  action: 'SEND_REMINDER',
                  reason: msg.data.reason || 'Deadline approaching for task.',
                  signals: msg.data.signals || [],
                  target: `@${msg.data.owner}`,
                  timestamp: msg.data.timestamp || new Date().toISOString()
                }, ...prev]);
              }
              break;

            case 'item_escalated':
              if (msg.data && msg.data.item) {
                setItems(prev => prev.map(item => 
                  item.id === msg.data.item.id ? msg.data.item : item
                ));
                if (msg.data.event) {
                  setAgentEvents(prev => [msg.data.event, ...prev]);
                }
              }
              break;

            case 'item_updated':
              if (msg.data && msg.data.id) {
                setItems(prev => prev.map(item => item.id === msg.data.id ? msg.data : item));
                if (selectedTask && selectedTask.id === msg.data.id) {
                  setSelectedTask(msg.data);
                }
              }
              break;

            case 'item_completed':
              if (msg.data && msg.data.id) {
                setItems(prev => prev.map(item => 
                  item.id === msg.data.id ? { ...item, status: 'completed' } : item
                ));
                if (selectedTask && selectedTask.id === msg.data.id) {
                  setSelectedTask(prev => prev ? { ...prev, status: 'completed' } : null);
                }
              }
              break;

            case 'agent_event':
              if (msg.data) {
                setAgentEvents(prev => [msg.data, ...prev]);
              }
              break;

            case 'meeting_reset':
              setSummary(null);
              setItems([]);
              setDecisions([]);
              setRisksBlockers([]);
              setAgentEvents([]);
              setIsExtracting(false);
              setAnalysisStageIndex(-1);
              break;

            default:
              break;
          }
        } catch (err) {
          console.error('[WebSocket] Event parse error:', err);
        }
      };

      ws.onclose = () => {
        setWsConnected(false);
        reconnectTimeout = setTimeout(connectWebSocket, 3000);
      };

      ws.onerror = (err) => {
        console.error('[WebSocket] Error:', err);
        ws.close();
      };
    };

    connectWebSocket();

    return () => {
      if (reconnectTimeout) clearTimeout(reconnectTimeout);
      if (ws) ws.close();
    };
  }, [meetingId]);

  // REST Action Handlers
  const handleSubmitTranscript = async (text) => {
    setIsExtracting(true);
    setAnalysisStageIndex(0);
    try {
      await fetch(`${API_BASE}/transcript/${meetingId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      });
    } catch (err) {
      console.error('Submit transcript error:', err);
      setIsExtracting(false);
    }
  };

  const handleMarkComplete = async (itemId) => {
    try {
      await fetch(`${API_BASE}/meeting/${meetingId}/items/${itemId}/complete`, {
        method: 'POST'
      });
    } catch (err) {
      console.error('Mark complete error:', err);
    }
  };

  const handleConfirmItem = async (itemId) => {
    try {
      await fetch(`${API_BASE}/meeting/${meetingId}/items/${itemId}/confirm`, {
        method: 'POST'
      });
    } catch (err) {
      console.error('Confirm item error:', err);
    }
  };

  const handleUpdateItem = async (itemId, updates) => {
    try {
      await fetch(`${API_BASE}/meeting/${meetingId}/items/${itemId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates)
      });
    } catch (err) {
      console.error('Update item error:', err);
    }
  };

  const handleAddManualItem = async (newItemData) => {
    try {
      await fetch(`${API_BASE}/meeting/${meetingId}/items`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newItemData)
      });
    } catch (err) {
      console.error('Add manual item error:', err);
    }
  };

  const handleResetMeeting = async () => {
    try {
      await fetch(`${API_BASE}/meeting/${meetingId}`, {
        method: 'DELETE'
      });
    } catch (err) {
      console.error('Reset meeting error:', err);
    }
  };

  const handleStartNewMeeting = () => {
    const newId = `meeting_${Date.now()}`;
    setMeetingId(newId);
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#F7F8FA] text-slate-900 selection:bg-indigo-500 selection:text-white">
      
      {/* Light Header */}
      <Header
        wsConnected={wsConnected}
        activeTab={activeNavTab}
        setActiveTab={setActiveNavTab}
        onResetMeeting={handleResetMeeting}
        onOpenMeetings={() => setIsHistoryOpen(true)}
      />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 space-y-6">
        
        {/* Hero Banner */}
        <DashboardHero onNewMeetingClick={handleStartNewMeeting} />

        {/* Metrics Grid */}
      {/* Upload Recording Section */}
      <div className="flex items-center gap-4 mt-4">
        <input
          type="file"
          accept="audio/*,video/*"
          onChange={e => setUploadFile(e.target.files[0])}
          className="border rounded p-1"
        />
        <button
          onClick={handleUploadRecording}
          className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 transition"
        >
          Upload Recording
        </button>
      </div>
        <StatsOverview items={items} decisions={decisions} risksBlockers={risksBlockers} />

        {/* Transcript Input Panel with Stage Checklist */}
        <TranscriptInput
          onSubmitTranscript={handleSubmitTranscript}
          isExtracting={isExtracting}
          analysisStageIndex={analysisStageIndex}
        />

        {/* AI Meeting Summary Card */}
        {summary && <MeetingSummaryCard summary={summary} />}

        {/* Workspace Grid: Main Workspace (70%) + Agent Activity Timeline (30%) */}
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

          <div className="lg:col-span-1">
            <ReminderFeed events={agentEvents} />
          </div>
        </div>

      </main>

      {/* Task Details & Source Evidence Drawer */}
      <TaskDetailDrawer
        item={selectedTask}
        onClose={() => setSelectedTask(null)}
        onUpdateItem={handleUpdateItem}
        onMarkComplete={handleMarkComplete}
      />

      {/* Multi-Meeting History Sidebar */}
      <MeetingHistorySidebar
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
        onSelectMeeting={(mId) => setMeetingId(mId)}
        onNewMeeting={handleStartNewMeeting}
      />

      {/* Light SaaS Footer */}
      <footer className="border-t border-slate-200 py-4 px-6 text-center text-xs text-slate-500 bg-white">
        AI Meeting & Follow-Up Agent — InnovaHack Chapter-1 | Agentic AI Workflow
      </footer>

    </div>
  );
}
