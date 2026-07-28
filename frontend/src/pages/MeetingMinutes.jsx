import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { FileText, Download, ArrowLeft, CheckCircle, File, FileCode } from 'lucide-react';

export default function MeetingMinutes() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [minutes, setMinutes] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (id) {
      fetchMinutes();
    }
  }, [id]);

  const fetchMinutes = async () => {
    setLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/meetings/${id}/minutes`);
      if (res.ok) {
        const data = await res.json();
        setMinutes(data.minutes);
      } else {
        // Not generated yet
        setMinutes(null);
      }
    } catch (e) {
      setError("Failed to fetch meeting minutes.");
    }
    setLoading(false);
  };

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/meetings/${id}/minutes`, { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        setMinutes(data.minutes);
      } else {
        setError("Failed to generate minutes.");
      }
    } catch (e) {
      setError("Error generating minutes.");
    }
    setLoading(false);
  };

  const handleExport = (format) => {
    window.location.href = `http://localhost:8000/api/meetings/${id}/export/${format}`;
  };

  if (!id) {
    return (
      <div className="p-8 text-center text-slate-500">
        <p>Please select a meeting from the Calendar or History to view its minutes.</p>
        <button onClick={() => navigate('/history')} className="mt-4 text-indigo-600 underline">Go to History</button>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="flex items-center gap-4 mb-8">
        <button onClick={() => navigate(-1)} className="p-2 text-slate-500 hover:text-slate-800 bg-slate-100 rounded-full">
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <FileText className="w-7 h-7 text-indigo-600" />
            Meeting Minutes
          </h1>
          <p className="text-slate-500 mt-1">Professional meeting documentation</p>
        </div>
      </div>

      {error && <div className="p-4 bg-red-50 text-red-600 rounded-lg mb-6">{error}</div>}

      {!minutes ? (
        <div className="text-center py-16 bg-white border border-slate-200 rounded-xl shadow-sm">
          <FileText className="w-16 h-16 mx-auto mb-4 text-slate-300" />
          <h2 className="text-xl font-semibold text-slate-800 mb-2">No Minutes Generated</h2>
          <p className="text-slate-500 mb-6 max-w-md mx-auto">
            Professional meeting minutes have not been generated for this meeting yet. Click below to generate them using AI.
          </p>
          <button 
            onClick={handleGenerate}
            disabled={loading}
            className="px-6 py-3 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition-colors disabled:opacity-50"
          >
            {loading ? 'Generating...' : 'Generate Minutes'}
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="md:col-span-3 bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
            <div className="p-8 prose prose-slate max-w-none">
               <pre className="whitespace-pre-wrap font-sans text-sm text-slate-700">
                 {minutes.content}
               </pre>
            </div>
          </div>
          
          <div className="md:col-span-1 space-y-4">
            <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
              <h3 className="font-semibold text-slate-800 mb-4 flex items-center gap-2">
                <Download className="w-5 h-5" /> Export Options
              </h3>
              
              <div className="space-y-3">
                <button onClick={() => handleExport('pdf')} className="w-full flex items-center gap-3 p-3 text-left bg-slate-50 border border-slate-100 hover:border-red-300 hover:bg-red-50 rounded-lg transition-colors">
                  <File className="w-5 h-5 text-red-500" />
                  <span className="font-medium text-slate-700">PDF Document</span>
                </button>
                
                <button onClick={() => handleExport('docx')} className="w-full flex items-center gap-3 p-3 text-left bg-slate-50 border border-slate-100 hover:border-blue-300 hover:bg-blue-50 rounded-lg transition-colors">
                  <FileText className="w-5 h-5 text-blue-500" />
                  <span className="font-medium text-slate-700">Word (DOCX)</span>
                </button>
                
                <button onClick={() => handleExport('md')} className="w-full flex items-center gap-3 p-3 text-left bg-slate-50 border border-slate-100 hover:border-slate-300 hover:bg-slate-100 rounded-lg transition-colors">
                  <FileCode className="w-5 h-5 text-slate-600" />
                  <span className="font-medium text-slate-700">Markdown</span>
                </button>

                <button onClick={() => handleExport('txt')} className="w-full flex items-center gap-3 p-3 text-left bg-slate-50 border border-slate-100 hover:border-slate-300 hover:bg-slate-100 rounded-lg transition-colors">
                  <FileText className="w-5 h-5 text-slate-500" />
                  <span className="font-medium text-slate-700">Plain Text</span>
                </button>
              </div>
            </div>
            
            <div className="bg-green-50 border border-green-200 rounded-xl p-4 flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
              <div>
                <h4 className="font-medium text-green-800">Generated Successfully</h4>
                <p className="text-xs text-green-700 mt-1">Last updated: {new Date(minutes.created_at).toLocaleString()}</p>
              </div>
              <button 
                onClick={handleGenerate} 
                disabled={loading}
                className="w-full mt-4 flex justify-center items-center gap-2 py-2.5 bg-indigo-50 text-indigo-700 hover:bg-indigo-100 rounded-lg font-medium transition-colors"
              >
                {loading ? 'Regenerating...' : 'Regenerate Minutes'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
