import React, { useEffect, useState } from 'react';
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
