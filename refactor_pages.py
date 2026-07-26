import os

base_dir = r"d:\MeetMind--main\frontend\src\pages"

files = {
    "Dashboard.jsx": """import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useMeeting } from '../context/MeetingContext';
import DashboardHero from '../components/DashboardHero';
import StatsOverview from '../components/StatsOverview';

export default function Dashboard() {
  const { items, decisions, risksBlockers, setMeetingId } = useMeeting();
  const [meetings, setMeetings] = useState([]);

  useEffect(() => {
    fetch('/api/meetings')
      .then(res => res.json())
      .then(data => setMeetings(data.slice(0, 5)))
      .catch(err => console.error(err));
  }, []);

  const handleStartNewMeeting = () => {
    setMeetingId(`meeting_${Date.now()}`);
  };

  return (
    <div className="space-y-6">
      <DashboardHero onNewMeetingClick={handleStartNewMeeting} />
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Link to="/live" onClick={handleStartNewMeeting} className="p-4 bg-white border border-slate-200 rounded-xl shadow-sm hover:border-indigo-300 hover:shadow-md transition-all flex flex-col items-center justify-center text-center gap-2 group">
          <div className="w-12 h-12 bg-indigo-50 text-indigo-600 rounded-full flex items-center justify-center group-hover:scale-110 transition-transform">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" /></svg>
          </div>
          <h3 className="font-semibold text-slate-800">Start Live Meeting</h3>
        </Link>
        <Link to="/record" className="p-4 bg-white border border-slate-200 rounded-xl shadow-sm hover:border-indigo-300 hover:shadow-md transition-all flex flex-col items-center justify-center text-center gap-2 group">
          <div className="w-12 h-12 bg-rose-50 text-rose-600 rounded-full flex items-center justify-center group-hover:scale-110 transition-transform">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" /></svg>
          </div>
          <h3 className="font-semibold text-slate-800">Record Audio</h3>
        </Link>
        <Link to="/upload" className="p-4 bg-white border border-slate-200 rounded-xl shadow-sm hover:border-indigo-300 hover:shadow-md transition-all flex flex-col items-center justify-center text-center gap-2 group">
          <div className="w-12 h-12 bg-emerald-50 text-emerald-600 rounded-full flex items-center justify-center group-hover:scale-110 transition-transform">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" /></svg>
          </div>
          <h3 className="font-semibold text-slate-800">Upload Recording</h3>
        </Link>
      </div>

      <StatsOverview items={items} decisions={decisions} risksBlockers={risksBlockers} />

      <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6">
        <h3 className="text-lg font-semibold text-slate-800 mb-4">Recent Meetings</h3>
        {meetings.length === 0 ? (
          <p className="text-slate-500 text-sm">No recent meetings found.</p>
        ) : (
          <div className="space-y-3">
            {meetings.map(m => (
              <div key={m.id} className="flex items-center justify-between p-3 border border-slate-100 rounded-lg hover:bg-slate-50">
                <div>
                  <p className="font-medium text-slate-800">{m.title}</p>
                  <p className="text-xs text-slate-500">{new Date(m.created_at).toLocaleString()}</p>
                </div>
                <Link to="/live" onClick={() => setMeetingId(m.id)} className="text-indigo-600 text-sm font-medium hover:underline">
                  View
                </Link>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
""",
    "LiveMeeting.jsx": """import React, { useState } from 'react';
import { useMeeting } from '../context/MeetingContext';
import TranscriptInput from '../components/TranscriptInput';
import MeetingSummaryCard from '../components/MeetingSummaryCard';
import ActionItemsTable from '../components/ActionItemsTable';
import ReminderFeed from '../components/ReminderFeed';
import TaskDetailDrawer from '../components/TaskDetailDrawer';

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

      <TranscriptInput
        onSubmitTranscript={handleSubmitTranscript}
        isExtracting={isExtracting}
        analysisStageIndex={analysisStageIndex}
      />

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
        <div className="lg:col-span-1">
          <ReminderFeed events={agentEvents} />
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
""",
    "UploadRecording.jsx": """import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMeeting } from '../context/MeetingContext';

export default function UploadRecording() {
  const [uploadFile, setUploadFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const { setMeetingId } = useMeeting();
  const navigate = useNavigate();

  const handleUploadRecording = async () => {
    if (!uploadFile) return;
    setIsUploading(true);
    const form = new FormData();
    form.append('file', uploadFile);
    try {
      const res = await fetch(`/api/meeting/upload`, {
        method: 'POST',
        body: form,
      });
      const data = await res.json();
      if (data.meeting_id) {
        setMeetingId(data.meeting_id);
        navigate('/live');
      }
    } catch (err) {
      alert(`Failed to upload recording: ${err.message || 'Server error'}`);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-slate-800">Upload Recording</h1>
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-8 text-center">
        <div className="w-16 h-16 bg-indigo-50 text-indigo-600 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" /></svg>
        </div>
        <h3 className="text-lg font-semibold text-slate-800 mb-2">Upload Audio or Video</h3>
        <p className="text-sm text-slate-500 mb-6">Supports MP3, WAV, MP4, WEBM, FLAC.</p>
        
        <input
          type="file"
          id="file-upload"
          accept="audio/*,video/*"
          onChange={e => setUploadFile(e.target.files[0])}
          className="hidden"
        />
        <label
          htmlFor="file-upload"
          className="inline-block px-6 py-3 bg-slate-50 border border-slate-300 rounded-lg font-medium text-slate-700 hover:bg-slate-100 cursor-pointer transition-colors shadow-sm mb-4"
        >
          {uploadFile ? uploadFile.name : 'Choose File'}
        </label>
        
        <div className="block mt-4">
          <button
            onClick={handleUploadRecording}
            disabled={!uploadFile || isUploading}
            className={`px-8 py-3 rounded-lg font-medium transition-all shadow-sm ${uploadFile && !isUploading ? 'bg-indigo-600 text-white hover:bg-indigo-700' : 'bg-slate-100 text-slate-400 cursor-not-allowed'}`}
          >
            {isUploading ? 'Uploading & Processing...' : 'Upload & Analyze'}
          </button>
        </div>
      </div>
    </div>
  );
}
""",
    "RecordAudio.jsx": """import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMeeting } from '../context/MeetingContext';

export default function RecordAudio() {
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [duration, setDuration] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);
  
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  const timerRef = useRef(null);
  
  const { setMeetingId } = useMeeting();
  const navigate = useNavigate();

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      mediaRecorder.onstop = handleStop;

      mediaRecorder.start();
      setIsRecording(true);
      setIsPaused(false);
      
      timerRef.current = setInterval(() => {
        setDuration(prev => prev + 1);
      }, 1000);
    } catch (err) {
      alert("Could not access microphone: " + err.message);
    }
  };

  const pauseRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.pause();
      setIsPaused(true);
      clearInterval(timerRef.current);
    }
  };

  const resumeRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'paused') {
      mediaRecorderRef.current.resume();
      setIsPaused(false);
      timerRef.current = setInterval(() => {
        setDuration(prev => prev + 1);
      }, 1000);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
      setIsRecording(false);
      setIsPaused(false);
      clearInterval(timerRef.current);
    }
  };

  const handleStop = async () => {
    setIsProcessing(true);
    const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
    const file = new File([blob], 'browser_recording.webm', { type: 'audio/webm' });
    const form = new FormData();
    form.append('file', file);
    
    try {
      const res = await fetch(`/api/meeting/upload`, {
        method: 'POST',
        body: form,
      });
      const data = await res.json();
      if (data.meeting_id) {
        setMeetingId(data.meeting_id);
        navigate('/live');
      }
    } catch (err) {
      alert(`Upload failed: ${err.message}`);
    } finally {
      setIsProcessing(false);
      setDuration(0);
    }
  };

  const formatTime = (secs) => {
    const m = Math.floor(secs / 60).toString().padStart(2, '0');
    const s = (secs % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-slate-800">Record Audio</h1>
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-8 text-center">
        
        <div className={`w-32 h-32 mx-auto rounded-full flex items-center justify-center border-4 mb-6 transition-all ${isRecording && !isPaused ? 'border-rose-500 bg-rose-50 animate-pulse' : 'border-slate-200 bg-slate-50'}`}>
          <div className="text-4xl font-mono text-slate-800">{formatTime(duration)}</div>
        </div>

        {isProcessing ? (
          <p className="text-indigo-600 font-medium animate-pulse">Processing Recording...</p>
        ) : (
          <div className="flex justify-center gap-4">
            {!isRecording ? (
              <button onClick={startRecording} className="px-8 py-3 bg-rose-600 text-white rounded-lg font-medium hover:bg-rose-700 shadow-sm shadow-rose-200">
                Start Recording
              </button>
            ) : (
              <>
                {isPaused ? (
                  <button onClick={resumeRecording} className="px-8 py-3 bg-emerald-600 text-white rounded-lg font-medium hover:bg-emerald-700">
                    Resume
                  </button>
                ) : (
                  <button onClick={pauseRecording} className="px-8 py-3 bg-amber-500 text-white rounded-lg font-medium hover:bg-amber-600">
                    Pause
                  </button>
                )}
                <button onClick={stopRecording} className="px-8 py-3 bg-slate-800 text-white rounded-lg font-medium hover:bg-slate-900">
                  Stop & Process
                </button>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
""",
    "MeetingHistory.jsx": """import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMeeting } from '../context/MeetingContext';

export default function MeetingHistory() {
  const [meetings, setMeetings] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const { setMeetingId } = useMeeting();
  const navigate = useNavigate();

  useEffect(() => {
    fetchMeetings();
  }, []);

  const fetchMeetings = () => {
    fetch('/api/meetings')
      .then(res => res.json())
      .then(data => setMeetings(data))
      .catch(err => console.error(err));
  };

  const handleDelete = async (id) => {
    if (confirm("Are you sure you want to delete this meeting?")) {
      await fetch(`/api/meeting/${id}`, { method: 'DELETE' });
      fetchMeetings();
    }
  };

  const filtered = meetings.filter(m => m.title.toLowerCase().includes(searchTerm.toLowerCase()));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-800">Meeting History</h1>
        <input 
          type="text" 
          placeholder="Search meetings..." 
          className="px-4 py-2 border border-slate-300 rounded-lg text-sm"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-medium">
            <tr>
              <th className="px-6 py-3">Title</th>
              <th className="px-6 py-3">Date</th>
              <th className="px-6 py-3">Language</th>
              <th className="px-6 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {filtered.map(m => (
              <tr key={m.id} className="hover:bg-slate-50 transition-colors">
                <td className="px-6 py-4 font-medium text-slate-800">{m.title}</td>
                <td className="px-6 py-4 text-slate-500">{new Date(m.created_at).toLocaleString()}</td>
                <td className="px-6 py-4 text-slate-500">{m.original_language || 'en'}</td>
                <td className="px-6 py-4 text-right space-x-3">
                  <button onClick={() => { setMeetingId(m.id); navigate('/live'); }} className="text-indigo-600 hover:underline font-medium">Open</button>
                  <button onClick={() => handleDelete(m.id)} className="text-red-500 hover:underline font-medium">Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {filtered.length === 0 && <div className="p-8 text-center text-slate-500">No meetings found.</div>}
      </div>
    </div>
  );
}
""",
    "AiChat.jsx": """import React, { useState } from 'react';

export default function AiChat() {
  const [messages, setMessages] = useState([{ role: 'agent', content: 'Hello! I am your Meeting AI Assistant. Ask me anything about your past meetings (e.g. "What tasks were assigned yesterday?").' }]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    
    const userMsg = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setIsLoading(true);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userMsg.content })
      });
      const data = await res.json();
      setMessages(prev => [...prev, { role: 'agent', content: data.answer }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'agent', content: 'Sorry, I encountered an error connecting to the AI.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="h-full flex flex-col max-w-4xl mx-auto bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
      <div className="p-4 border-b border-slate-200 bg-slate-50">
        <h2 className="text-lg font-bold text-slate-800">AI Meeting Assistant</h2>
        <p className="text-sm text-slate-500">Query your entire meeting history.</p>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] p-3 rounded-xl ${m.role === 'user' ? 'bg-indigo-600 text-white rounded-br-none' : 'bg-slate-100 text-slate-800 rounded-bl-none'}`}>
              {m.content}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-slate-100 text-slate-500 p-3 rounded-xl rounded-bl-none animate-pulse">
              Thinking...
            </div>
          </div>
        )}
      </div>

      <form onSubmit={sendMessage} className="p-4 border-t border-slate-200 bg-white flex gap-2">
        <input
          type="text"
          className="flex-1 px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
          placeholder="Ask a question..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <button type="submit" disabled={isLoading} className="px-6 py-2 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-50">
          Send
        </button>
      </form>
    </div>
  );
}
""",
    "Analytics.jsx": """import React from 'react';

export default function Analytics() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-800">Analytics</h1>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-6 bg-white rounded-xl shadow-sm border border-slate-200">
          <p className="text-sm text-slate-500 font-medium">Total Meetings</p>
          <p className="text-3xl font-bold text-slate-800 mt-2">24</p>
        </div>
        <div className="p-6 bg-white rounded-xl shadow-sm border border-slate-200">
          <p className="text-sm text-slate-500 font-medium">Recording Time</p>
          <p className="text-3xl font-bold text-slate-800 mt-2">12.5 hrs</p>
        </div>
        <div className="p-6 bg-white rounded-xl shadow-sm border border-slate-200">
          <p className="text-sm text-slate-500 font-medium">Languages</p>
          <p className="text-3xl font-bold text-slate-800 mt-2">3</p>
        </div>
        <div className="p-6 bg-white rounded-xl shadow-sm border border-slate-200">
          <p className="text-sm text-slate-500 font-medium">Action Items</p>
          <p className="text-3xl font-bold text-slate-800 mt-2">142</p>
        </div>
      </div>
      <div className="p-8 bg-white rounded-xl shadow-sm border border-slate-200 flex items-center justify-center h-64">
        <p className="text-slate-500">Charts placeholder (Chart.js / Recharts integration)</p>
      </div>
    </div>
  );
}
""",
    "Settings.jsx": """import React from 'react';

export default function Settings() {
  return (
    <div className="max-w-2xl space-y-6">
      <h1 className="text-2xl font-bold text-slate-800">Settings</h1>
      
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 divide-y divide-slate-100">
        <div className="p-6 flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-slate-800">Dark Mode</h3>
            <p className="text-sm text-slate-500">Toggle system theme.</p>
          </div>
          <button className="w-12 h-6 bg-slate-200 rounded-full relative transition-colors">
            <div className="w-5 h-5 bg-white rounded-full absolute top-0.5 left-0.5 shadow-sm"></div>
          </button>
        </div>
        
        <div className="p-6 flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-slate-800">Default Language</h3>
            <p className="text-sm text-slate-500">Set primary recording language.</p>
          </div>
          <select className="border border-slate-300 rounded-md px-3 py-1.5 text-sm">
            <option>English</option>
            <option>Spanish</option>
            <option>French</option>
          </select>
        </div>
        
        <div className="p-6 flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-slate-800">AI Notifications</h3>
            <p className="text-sm text-slate-500">Receive reminders for pending action items.</p>
          </div>
          <button className="w-12 h-6 bg-indigo-600 rounded-full relative transition-colors">
            <div className="w-5 h-5 bg-white rounded-full absolute top-0.5 right-0.5 shadow-sm"></div>
          </button>
        </div>
      </div>
    </div>
  );
}
"""
}

for path, content in files.items():
    full_path = os.path.join(base_dir, path)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Pages refactored.")
