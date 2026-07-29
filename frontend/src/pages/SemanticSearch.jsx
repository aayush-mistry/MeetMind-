import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

export default function SemanticSearch() {
  const navigate = useNavigate();
  const location = useLocation();
  
  const [query, setQuery] = useState(location.state?.query || '');
  const [results, setResults] = useState([]);
  const [answer, setAnswer] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [filterType, setFilterType] = useState('');
  
  useEffect(() => {
    if (location.state?.query) {
      setQuery(location.state.query);
      handleSearch(null, location.state.query);
    }
  }, [location.state?.query]);

  const handleSearch = async (e, initialQuery = null) => {
    if (e) e.preventDefault();
    const searchQuery = initialQuery || query;
    if (!searchQuery.trim()) return;

    setIsLoading(true);
    setAnswer('');
    setResults([]);

    const filters = {};
    if (filterType) {
      filters.type = filterType;
    }

    try {
      const res = await fetch('http://localhost:8000/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: searchQuery, filters: Object.keys(filters).length ? filters : null })
      });
      const data = await res.json();
      setAnswer(data.answer);
      setResults(data.results || []);
    } catch (err) {
      setAnswer("An error occurred while searching. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto py-8 px-4 h-full flex flex-col">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-800 mb-2">Semantic AI Search</h1>
        <p className="text-slate-500">Search across all your meetings using natural language. Ask questions, find decisions, and locate action items instantly.</p>
      </div>

      <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 mb-8">
        <form onSubmit={handleSearch} className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <input 
              type="text" 
              placeholder="e.g. What did Rahul say about authentication?"
              className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all text-lg"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>
          <div className="w-48">
            <select 
              className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500"
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
            >
              <option value="">All Sources</option>
              <option value="transcript_chunk">Transcript Only</option>
              <option value="action_item">Action Items</option>
              <option value="decision">Decisions</option>
              <option value="risk">Risks & Blockers</option>
              <option value="topic">Topics</option>
            </select>
          </div>
          <button 
            type="submit"
            disabled={isLoading || !query.trim()}
            className="px-8 py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center min-w-[120px]"
          >
            {isLoading ? 'Searching...' : 'Search'}
          </button>
        </form>
        
        <div className="mt-4 flex gap-2 flex-wrap">
          <span className="text-sm text-slate-500 py-1">Try:</span>
          {["What decisions were made about the database?", "Show me action items for frontend", "When is the next release?"].map(s => (
            <button 
              key={s} 
              onClick={() => { setQuery(s); }}
              className="text-xs px-3 py-1 bg-indigo-50 text-indigo-600 rounded-full hover:bg-indigo-100 transition-colors"
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {(answer || isLoading) && (
        <div className="flex-1 flex flex-col gap-6 overflow-hidden">
          
          <div className="bg-indigo-50 p-6 rounded-2xl border border-indigo-100">
            <h3 className="font-semibold text-indigo-900 mb-2 flex items-center gap-2">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
              AI Answer
            </h3>
            {isLoading ? (
              <div className="animate-pulse flex space-x-4">
                <div className="flex-1 space-y-3 py-1">
                  <div className="h-4 bg-indigo-200 rounded w-3/4"></div>
                  <div className="h-4 bg-indigo-200 rounded"></div>
                  <div className="h-4 bg-indigo-200 rounded w-5/6"></div>
                </div>
              </div>
            ) : (
              <div className="text-slate-800 whitespace-pre-wrap leading-relaxed">{answer}</div>
            )}
          </div>

          {results.length > 0 && (
            <div>
              <h3 className="font-semibold text-slate-800 mb-4 px-1">Sources & Citations ({results.length})</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {results.map((res, idx) => (
                  <div key={idx} className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <h4 className="font-semibold text-slate-800">{res.title}</h4>
                        <div className="text-xs text-slate-500 mt-1">{new Date(res.date).toLocaleDateString()}</div>
                      </div>
                      <div className="flex flex-col items-end gap-1">
                        <span className="text-[10px] font-bold px-2 py-1 bg-green-100 text-green-700 rounded-full">
                          {res.confidence}% Match
                        </span>
                        <span className="text-[10px] px-2 py-1 bg-slate-100 text-slate-600 rounded-full uppercase tracking-wider">
                          {res.source_type}
                        </span>
                      </div>
                    </div>
                    
                    {res.matched_topic && (
                      <div className="mb-2">
                        <span className="text-xs font-medium text-indigo-600 bg-indigo-50 px-2 py-1 rounded">Topic: {res.matched_topic}</span>
                      </div>
                    )}
                    
                    <div className="bg-slate-50 p-3 rounded-lg text-sm text-slate-700 italic border-l-4 border-slate-300 line-clamp-3 mb-4">
                      "{res.snippet}"
                    </div>
                    
                    <div className="flex gap-2 mt-auto">
                      <button 
                        onClick={() => navigate(`/minutes/${res.meeting_id}`)}
                        className="flex-1 py-2 text-sm font-medium text-indigo-600 bg-indigo-50 hover:bg-indigo-100 rounded-lg transition-colors"
                      >
                        Open Meeting
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
