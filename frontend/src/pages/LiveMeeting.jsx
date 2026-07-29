import React, { useState, useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import { useMeeting } from '../context/MeetingContext';
import MeetingSummaryCard from '../components/MeetingSummaryCard';
import ActionItemsTable from '../components/ActionItemsTable';
import ReminderFeed from '../components/ReminderFeed';
import TaskDetailDrawer from '../components/TaskDetailDrawer';
import SpeakersList from '../components/SpeakersList';
import TopicsDashboard from './TopicsDashboard';
import TranscriptView from '../components/TranscriptView';

const API_BASE = '/api';

export default function LiveMeeting() {
  const location = useLocation();
  const event = location.state?.event;

  const {
    meetingId, setMeetingId,
    summary, items, decisions, risksBlockers, agentEvents,
    isExtracting, analysisStageIndex, wsConnected,
    setIsExtracting, setAnalysisStageIndex
  } = useMeeting();

  const [selectedTask, setSelectedTask] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  // Recording State
  const [isRecording, setIsRecording] = useState(false);
  const [duration, setDuration] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);
  
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  const timerRef = useRef(null);
  const initializedEventIdRef = useRef(null);

  useEffect(() => {
    if (event && event.id !== initializedEventIdRef.current) {
      initializedEventIdRef.current = event.id;
      initLiveMeeting(event);
    }
    
    return () => {
        if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [event]);

  const initLiveMeeting = async (evt) => {
    try {
      const res = await fetch(`${API_BASE}/meeting/init`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: evt.title, description: `Live meeting for ${evt.title} with ${evt.participants || 'participants'}` })
      });
      
      if (!res.ok) throw new Error("Failed to initialize meeting");
      const data = await res.json();
      const newMeetingId = data.meeting_id;
      
      setMeetingId(newMeetingId); 

      if (evt.event_id || evt.id) {
         const eventId = evt.event_id || evt.id;
         await fetch(`${API_BASE}/calendar/link/${newMeetingId}/${eventId}`, { method: 'POST' });
      }

      startRecording();
    } catch (err) {
      console.error("Initialization error:", err);
      alert("Failed to start live meeting: " + err.message);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      mediaRecorder.start();
      setIsRecording(true);
      
      timerRef.current = setInterval(() => {
        setDuration(prev => prev + 1);
      }, 1000);
    } catch (err) {
      console.error('Could not access microphone:', err);
      alert("Could not access microphone: " + err.message);
    }
  };

  const stopMeeting = async () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
      setIsRecording(false);
      clearInterval(timerRef.current);
      
      setIsProcessing(true);
      
      const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
      const file = new File([blob], 'live_recording.webm', { type: 'audio/webm' });
      const form = new FormData();
      form.append('file', file);
      form.append('meeting_id', meetingId);

      try {
        const res = await fetch(`${API_BASE}/meeting/upload`, {
          method: 'POST',
          body: form,
        });
        if (!res.ok) throw new Error(await res.text());
      } catch (err) {
        console.error('Upload error:', err);
        alert(`Upload failed: ${err.message}`);
      } finally {
        setIsProcessing(false);
      }
    }
  };

  const formatTime = (secs) => {
    const m = Math.floor(secs / 60).toString().padStart(2, '0');
    const s = (secs % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  };



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
        <div>
          <h1 className="text-2xl font-bold text-slate-800">
             {event ? `Live: ${event.title}` : `Live Meeting: `}
             {meetingId && <span className="text-indigo-600 text-sm ml-2">({meetingId})</span>}
          </h1>
          {event && (
             <p className="text-sm text-slate-500 mt-1">
               Participants: {event.participants || 'None'} | Platform: {event.platform}
             </p>
          )}
        </div>
        <div className="flex items-center gap-4">
          {(isRecording || isProcessing) && (
            <div className="flex items-center gap-3 bg-white px-4 py-2 rounded-full border border-slate-200 shadow-sm">
               {isRecording && !isProcessing && (
                  <div className="flex items-center gap-2 text-rose-600 font-medium">
                    <div className="w-2.5 h-2.5 rounded-full bg-rose-500 animate-pulse"></div>
                    {formatTime(duration)}
                  </div>
               )}
               {isProcessing && (
                  <div className="text-indigo-600 font-medium animate-pulse text-sm">
                    Processing AI...
                  </div>
               )}
               {isRecording && !isProcessing && (
                 <button onClick={stopMeeting} className="text-sm bg-rose-100 hover:bg-rose-200 text-rose-700 px-3 py-1 rounded-md transition-colors">
                   Stop Meeting
                 </button>
               )}
            </div>
          )}
          <div className="flex items-center gap-2 text-sm font-medium">
            <div className={`w-2.5 h-2.5 rounded-full ${wsConnected ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'}`}></div>
            <span className={wsConnected ? 'text-emerald-600' : 'text-red-500'}>
              {wsConnected ? 'Agent Connected' : 'Disconnected'}
            </span>
          </div>
        </div>
      </div>

      {summary && <MeetingSummaryCard summary={summary} />}

      <div className="border-b border-slate-200">
        <nav className="-mb-px flex gap-6">
          <button
            onClick={() => setActiveTab('overview')}
            className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'overview'
                ? 'border-indigo-500 text-indigo-600'
                : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
            }`}
          >
            Overview & Actions
          </button>
          <button
            onClick={() => setActiveTab('topics')}
            className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'topics'
                ? 'border-indigo-500 text-indigo-600'
                : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
            }`}
          >
            Topics
          </button>
          <button
            onClick={() => setActiveTab('transcript')}
            className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'transcript'
                ? 'border-indigo-500 text-indigo-600'
                : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
            }`}
          >
            Transcript
          </button>
        </nav>
      </div>

      {activeTab === 'overview' && (
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
      )}

      {activeTab === 'topics' && (
        <div className="-mx-6">
          <TopicsDashboard />
        </div>
      )}

      {activeTab === 'transcript' && (
        <div className="-mx-6">
          <TranscriptView meeting={meeting} />
        </div>
      )}

      <TaskDetailDrawer
        item={selectedTask}
        onClose={() => setSelectedTask(null)}
        onUpdateItem={handleUpdateItem}
        onMarkComplete={handleMarkComplete}
      />
    </div>
  );
}
