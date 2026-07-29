import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import LiveMeeting from './pages/LiveMeeting';
import RecordAudio from './pages/RecordAudio';
import UploadRecording from './pages/UploadRecording';
import MeetingHistory from './pages/MeetingHistory';
import AiChat from './pages/AiChat';
import Analytics from './pages/Analytics';
import Settings from './pages/Settings';
import CalendarDashboard from './pages/CalendarDashboard';
import MeetingMinutes from './pages/MeetingMinutes';
import TopicsDashboard from './pages/TopicsDashboard';
import SemanticSearch from './pages/SemanticSearch';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="live" element={<LiveMeeting />} />
        <Route path="record" element={<RecordAudio />} />
        <Route path="upload" element={<UploadRecording />} />
        <Route path="history" element={<MeetingHistory />} />
        <Route path="chat" element={<AiChat />} />
        <Route path="analytics" element={<Analytics />} />
        <Route path="settings" element={<Settings />} />
        <Route path="calendar" element={<CalendarDashboard />} />
        <Route path="minutes" element={<MeetingMinutes />} />
        <Route path="minutes/:id" element={<MeetingMinutes />} />
        <Route path="topics" element={<TopicsDashboard />} />
        <Route path="search" element={<SemanticSearch />} />
      </Route>
    </Routes>
  );
}
