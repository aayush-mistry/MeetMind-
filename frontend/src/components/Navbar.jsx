import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search } from 'lucide-react';

export default function Navbar() {
  const [query, setQuery] = useState('');
  const navigate = useNavigate();

  const handleSearch = (e) => {
    e.preventDefault();
    if(query.trim()) {
      navigate('/search', { state: { query } });
      setQuery('');
    }
  };

  return (
    <header className="bg-white border-b border-slate-200 h-16 flex items-center justify-between px-6 shrink-0">
      <div className="flex items-center gap-4 md:hidden">
        <h2 className="text-xl font-bold text-indigo-600">MeetMind</h2>
      </div>
      <div className="flex-1 flex justify-center max-w-2xl px-4 hidden md:flex">
        <form onSubmit={handleSearch} className="w-full relative">
          <Search className="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input 
            type="text" 
            placeholder="Search meetings, topics, decisions..."
            className="w-full pl-10 pr-4 py-2 bg-slate-100 border-none rounded-full focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </form>
      </div>
      <div className="flex items-center gap-4">
        <div className="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-600 font-bold">
          U
        </div>
      </div>
    </header>
  );
}
