import React, { useState, useEffect } from 'react';
import { Users, Edit2, Check, X, Clock, MessageSquare, BarChart2 } from 'lucide-react';

export default function SpeakersList({ meetingId, transcript }) {
  const [speakers, setSpeakers] = useState([]);
  const [mappings, setMappings] = useState([]);
  const [editingId, setEditingId] = useState(null);
  const [editName, setEditName] = useState('');

  // Very basic mock stats for demonstration
  const generateStats = (name) => {
    // In a real implementation, this would parse the transcript or be returned by backend
    return {
      speakingTime: Math.floor(Math.random() * 20) + 2, // 2-22 min
      percentage: Math.floor(Math.random() * 40) + 10, // 10-50%
      words: Math.floor(Math.random() * 2000) + 200,
      messages: Math.floor(Math.random() * 50) + 5
    };
  };

  useEffect(() => {
    // Extract generic speakers from transcript or use defaults if transcript is empty
    const foundSpeakers = ["Speaker 1", "Speaker 2"]; // Simplified for now
    
    // Fetch mappings
    if (meetingId) {
      fetch(`http://localhost:8000/api/meetings/${meetingId}/speakers`)
        .then(res => res.json())
        .then(data => {
           setMappings(data.mappings || []);
        })
        .catch(console.error);
    }
    
    // Merge
    const merged = foundSpeakers.map(fs => {
       const mapped = mappings.find(m => m.original_speaker === fs);
       return {
         original: fs,
         currentName: mapped ? mapped.mapped_speaker : fs,
         stats: generateStats(fs)
       };
    });
    setSpeakers(merged);
    
  }, [meetingId, mappings.length, transcript]);

  const handleSaveRename = async (original) => {
    if (!editName.trim()) {
      setEditingId(null);
      return;
    }
    
    try {
      const res = await fetch(`http://localhost:8000/api/meetings/${meetingId}/speakers`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          original_speaker: original,
          mapped_speaker: editName.trim()
        })
      });
      if (res.ok) {
        setMappings(prev => {
          const filtered = prev.filter(p => p.original_speaker !== original);
          return [...filtered, { original_speaker: original, mapped_speaker: editName.trim() }];
        });
      }
    } catch (e) {
      console.error(e);
    }
    setEditingId(null);
  };

  return (
    <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden flex flex-col h-full">
      <div className="p-4 border-b border-slate-200 bg-slate-50 flex justify-between items-center">
        <h2 className="font-semibold text-slate-800 flex items-center gap-2">
          <Users className="w-5 h-5 text-indigo-500" />
          Speaker Analytics
        </h2>
      </div>
      <div className="p-4 overflow-y-auto flex-1 space-y-4">
        {speakers.map((spk, idx) => (
          <div key={idx} className="p-4 border border-slate-100 bg-white rounded-lg shadow-sm hover:border-indigo-100 transition-colors">
            <div className="flex justify-between items-center mb-3">
              {editingId === spk.original ? (
                <div className="flex items-center gap-2">
                  <input 
                    type="text" 
                    value={editName} 
                    onChange={e => setEditName(e.target.value)}
                    className="border border-slate-300 rounded px-2 py-1 text-sm focus:outline-indigo-500 w-32"
                    autoFocus
                  />
                  <button onClick={() => handleSaveRename(spk.original)} className="text-emerald-600"><Check className="w-4 h-4"/></button>
                  <button onClick={() => setEditingId(null)} className="text-red-500"><X className="w-4 h-4"/></button>
                </div>
              ) : (
                <div className="flex items-center gap-2 group">
                  <div className="w-8 h-8 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold text-sm">
                    {spk.currentName.charAt(0)}
                  </div>
                  <h3 className="font-semibold text-slate-800">{spk.currentName}</h3>
                  <button 
                    onClick={() => { setEditingId(spk.original); setEditName(spk.currentName); }} 
                    className="text-slate-400 opacity-0 group-hover:opacity-100 hover:text-indigo-600 transition-all"
                  >
                    <Edit2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              )}
              <div className="text-xs font-medium text-slate-500 bg-slate-100 px-2 py-1 rounded-full">
                {spk.stats.percentage}% Speaking
              </div>
            </div>
            
            <div className="grid grid-cols-3 gap-2 text-center text-sm border-t border-slate-100 pt-3">
              <div>
                <p className="text-slate-400 text-xs flex justify-center mb-1"><Clock className="w-3.5 h-3.5" /></p>
                <p className="font-medium text-slate-700">{spk.stats.speakingTime}m</p>
              </div>
              <div>
                <p className="text-slate-400 text-xs flex justify-center mb-1"><MessageSquare className="w-3.5 h-3.5" /></p>
                <p className="font-medium text-slate-700">{spk.stats.messages}</p>
              </div>
              <div>
                <p className="text-slate-400 text-xs flex justify-center mb-1"><BarChart2 className="w-3.5 h-3.5" /></p>
                <p className="font-medium text-slate-700">{spk.stats.words}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
