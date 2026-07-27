import React, { useEffect, useState } from 'react';
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
                  <button onClick={() => navigate(`/minutes/${m.id}`)} className="text-emerald-600 hover:underline font-medium">Minutes</button>
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
