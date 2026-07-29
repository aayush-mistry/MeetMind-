import React, { useState } from 'react';

export default function TranscriptView({ meeting }) {
  const [viewOriginal, setViewOriginal] = useState(false);

  if (!meeting) {
    return <div className="p-8 text-center text-slate-500">No meeting data available.</div>;
  }

  const hasOriginal = meeting.original_transcript && meeting.original_language && meeting.original_language.toLowerCase() !== 'en' && meeting.original_language.toLowerCase() !== 'english';

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-slate-800">Meeting Transcript</h2>
        {hasOriginal && (
          <div className="flex items-center gap-3">
            <span className="text-sm font-medium text-slate-600 bg-slate-100 px-3 py-1 rounded-full border border-slate-200">
              Detected Language: {meeting.original_language}
            </span>
            <div className="flex bg-slate-100 p-1 rounded-lg">
              <button
                onClick={() => setViewOriginal(false)}
                className={`px-4 py-1.5 text-sm font-medium rounded-md transition-colors ${
                  !viewOriginal ? 'bg-white text-indigo-600 shadow-sm' : 'text-slate-500 hover:text-slate-700'
                }`}
              >
                English
              </button>
              <button
                onClick={() => setViewOriginal(true)}
                className={`px-4 py-1.5 text-sm font-medium rounded-md transition-colors ${
                  viewOriginal ? 'bg-white text-indigo-600 shadow-sm' : 'text-slate-500 hover:text-slate-700'
                }`}
              >
                Original
              </button>
            </div>
          </div>
        )}
      </div>

      <div className="bg-slate-50 rounded-lg p-4 max-h-[600px] overflow-y-auto whitespace-pre-wrap text-slate-700 font-mono text-sm leading-relaxed border border-slate-200">
        {viewOriginal && hasOriginal ? meeting.original_transcript : meeting.transcript}
      </div>
    </div>
  );
}
