import React, { useState } from 'react';

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
      const res = await fetch('http://localhost:8000/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userMsg.content })
      });
      const data = await res.json();
      setMessages(prev => [...prev, { role: 'agent', content: data.answer, results: data.results }]);
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
              <div className="whitespace-pre-wrap">{m.content}</div>
              {m.results && m.results.length > 0 && (
                <div className="mt-3 pt-3 border-t border-slate-200">
                  <p className="text-xs font-semibold mb-2">Sources:</p>
                  <div className="flex flex-col gap-2">
                    {m.results.map((r, idx) => (
                      <div key={idx} className="bg-white p-2 rounded border border-slate-200 text-xs">
                        <div className="font-semibold text-indigo-600">{r.title}</div>
                        <div className="text-slate-500 italic mt-1 text-[10px] line-clamp-2">"{r.snippet}"</div>
                        <div className="flex gap-2 mt-1">
                          <span className="text-[10px] bg-slate-100 px-1 rounded">{r.confidence}% match</span>
                          <span className="text-[10px] bg-slate-100 px-1 rounded">{r.source_type}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
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
