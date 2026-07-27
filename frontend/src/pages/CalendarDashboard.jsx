import React, { useState, useEffect } from 'react';
import { Calendar as CalendarIcon, Video, Link as LinkIcon, LogOut, Clock, Plus, Play, Download } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function CalendarDashboard() {
  const [providers, setProviders] = useState([]);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const fetchCalendarData = async () => {
    setLoading(true);
    try {
      const accRes = await fetch('http://localhost:8000/api/calendar/accounts');
      if (accRes.ok) {
        const data = await accRes.json();
        setProviders(data.connected_providers || []);
      }
      
      const evtRes = await fetch('http://localhost:8000/api/calendar/events');
      if (evtRes.ok) {
        const data = await evtRes.json();
        setEvents(data || []);
      }
    } catch (e) {
      console.error('Failed to fetch calendar data', e);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchCalendarData();
  }, []);

  const connectProvider = async (provider) => {
    try {
      const res = await fetch(`http://localhost:8000/api/calendar/auth/${provider}`);
      if (res.ok) {
        const data = await res.json();
        // Stub: directly call the callback url to simulate oauth
        await fetch(`http://localhost:8000${data.auth_url}`);
        fetchCalendarData();
      }
    } catch (e) {
      console.error(e);
    }
  };

  const disconnectProvider = async (provider) => {
    try {
      await fetch(`http://localhost:8000/api/calendar/accounts/${provider}`, { method: 'DELETE' });
      fetchCalendarData();
    } catch (e) {
      console.error(e);
    }
  };

  const handleStartMeeting = (event) => {
    navigate('/live', { state: { event } });
  };

  const handleGenerateMoM = (event) => {
    if (event.meeting_id) {
       navigate(`/minutes/${event.meeting_id}`);
    } else {
       alert("No meeting recording linked to this event yet. Please record the meeting first.");
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <CalendarIcon className="w-7 h-7 text-indigo-600" />
            Calendar & Meetings
          </h1>
          <p className="text-slate-500 mt-1">Manage your schedule and connected accounts.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="col-span-1 md:col-span-1 bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-800 mb-4">Integrations</h2>
          
          <div className="space-y-4">
            {/* Google Calendar */}
            <div className="flex items-center justify-between p-3 border border-slate-100 rounded-lg bg-slate-50">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center shadow-sm text-red-500 font-bold border border-slate-100">G</div>
                <div>
                  <p className="font-medium text-slate-800">Google Calendar</p>
                  <p className="text-xs text-slate-500">{providers.includes('google') ? 'Connected' : 'Not connected'}</p>
                </div>
              </div>
              {providers.includes('google') ? (
                <button onClick={() => disconnectProvider('google')} className="text-slate-400 hover:text-red-600 p-2"><LogOut className="w-4 h-4" /></button>
              ) : (
                <button onClick={() => connectProvider('google')} className="text-indigo-600 hover:bg-indigo-50 p-2 rounded"><LinkIcon className="w-4 h-4" /></button>
              )}
            </div>
            
            {/* Outlook Calendar */}
            <div className="flex items-center justify-between p-3 border border-slate-100 rounded-lg bg-slate-50">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center shadow-sm text-blue-500 font-bold border border-slate-100">O</div>
                <div>
                  <p className="font-medium text-slate-800">Outlook Calendar</p>
                  <p className="text-xs text-slate-500">{providers.includes('outlook') ? 'Connected' : 'Not connected'}</p>
                </div>
              </div>
              {providers.includes('outlook') ? (
                <button onClick={() => disconnectProvider('outlook')} className="text-slate-400 hover:text-red-600 p-2"><LogOut className="w-4 h-4" /></button>
              ) : (
                <button onClick={() => connectProvider('outlook')} className="text-indigo-600 hover:bg-indigo-50 p-2 rounded"><LinkIcon className="w-4 h-4" /></button>
              )}
            </div>
          </div>
        </div>

        <div className="col-span-1 md:col-span-2 bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold text-slate-800">Upcoming Meetings</h2>
            <button onClick={fetchCalendarData} className="text-sm text-indigo-600 hover:underline">Refresh</button>
          </div>
          
          {loading ? (
            <div className="text-center py-8 text-slate-500">Loading events...</div>
          ) : events.length === 0 ? (
            <div className="text-center py-8 text-slate-500">
              <CalendarIcon className="w-12 h-12 mx-auto mb-3 text-slate-300" />
              <p>No upcoming meetings found.</p>
              <p className="text-sm mt-1">Connect a calendar to sync events.</p>
            </div>
          ) : (
            <div className="space-y-4 max-h-[500px] overflow-y-auto pr-2">
              {events.map((evt) => (
                <div key={evt.id} className="p-4 border border-slate-200 rounded-xl hover:border-indigo-300 transition-colors flex flex-col sm:flex-row justify-between gap-4">
                  <div>
                    <h3 className="font-semibold text-slate-800">{evt.title}</h3>
                    <div className="flex items-center gap-4 mt-2 text-sm text-slate-500">
                      <span className="flex items-center gap-1"><Clock className="w-4 h-4" /> {new Date(evt.start_time).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                      <span className="flex items-center gap-1"><Video className="w-4 h-4" /> {evt.platform}</span>
                    </div>
                    <p className="text-sm text-slate-500 mt-2">Participants: {evt.participants || 'None'}</p>
                  </div>
                  
                  <div className="flex flex-col gap-2 justify-center sm:items-end">
                    <button 
                      onClick={() => handleStartMeeting(evt)}
                      className="flex items-center gap-1.5 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors"
                    >
                      <Play className="w-4 h-4" /> Start Live
                    </button>
                    <button 
                      onClick={() => handleGenerateMoM(evt)}
                      className="flex items-center gap-1.5 px-4 py-2 bg-slate-100 text-slate-700 rounded-lg text-sm font-medium hover:bg-slate-200 transition-colors"
                    >
                      <Download className="w-4 h-4" /> MoM & Summary
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
