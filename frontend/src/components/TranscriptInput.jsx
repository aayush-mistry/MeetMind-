import React, { useState, useEffect } from 'react';
import { FileText, Sparkles, Play, AlertCircle, CheckCircle2, Loader2 } from 'lucide-react';

export default function TranscriptInput({ 
  onSubmitTranscript, 
  isExtracting, 
  analysisStageIndex = -1 
}) {
  const [transcript, setTranscript] = useState('');
  const [sampleTranscripts, setSampleTranscripts] = useState({});
  const [selectedSample, setSelectedSample] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  const stagesList = [
    "Transcript received",
    "Detecting speakers & context",
    "Understanding discussion & summary",
    "Extracting explicit decisions",
    "Resolving commitments & owners",
    "Detecting risks & mapping dependencies",
    "Calculating AI confidence scores",
    "Finalizing results"
  ];

  useEffect(() => {
    fetch('http://localhost:8000/api/sample-transcripts')
      .then(res => res.json())
      .then(data => {
        setSampleTranscripts(data);
        if (data.product_sync) {
          setSelectedSample('product_sync');
          setTranscript(data.product_sync.text);
        }
      })
      .catch(err => console.log('Sample transcripts fetch error:', err));
  }, []);

  const handleSelectSample = (key) => {
    setSelectedSample(key);
    if (sampleTranscripts[key]) {
      setTranscript(sampleTranscripts[key].text);
      setErrorMsg('');
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!transcript.trim()) {
      setErrorMsg('Please enter or select a meeting transcript first.');
      return;
    }
    setErrorMsg('');
    onSubmitTranscript(transcript);
  };

  return (
    <div className="saas-card rounded-xl border border-slate-200 p-5 shadow-sm">
      
      {/* Header & Presets */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-indigo-50 text-indigo-600 border border-indigo-100">
            <FileText className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-slate-900">Meeting Transcript</h2>
            <p className="text-xs text-slate-500">Paste meeting notes or select a 1-click hackathon preset</p>
          </div>
        </div>

        {/* Preset Chips */}
        <div className="flex flex-wrap items-center gap-1.5">
          <span className="text-xs text-slate-500 font-medium mr-1 hidden sm:inline">Presets:</span>
          {Object.keys(sampleTranscripts).map((key) => {
            const sample = sampleTranscripts[key];
            const isSelected = selectedSample === key;
            return (
              <button
                key={key}
                type="button"
                onClick={() => handleSelectSample(key)}
                className={`px-3 py-1 text-xs rounded-lg font-medium transition border flex items-center gap-1 ${
                  isSelected
                    ? 'bg-indigo-600 text-white border-indigo-600 shadow-xs'
                    : 'bg-slate-100 text-slate-700 border-slate-200 hover:bg-slate-200/70'
                }`}
              >
                <Sparkles className="w-3 h-3 text-indigo-300" />
                <span>{sample.title}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Transcript Textarea Form */}
      <form onSubmit={handleSubmit} className="space-y-3">
        <div className="relative">
          <textarea
            value={transcript}
            onChange={(e) => {
              setTranscript(e.target.value);
              if (errorMsg) setErrorMsg('');
            }}
            placeholder="Paste raw meeting notes or conversation transcript here..."
            rows={5}
            className="w-full bg-slate-50/80 text-slate-800 text-xs sm:text-sm font-mono placeholder-slate-400 rounded-xl p-4 border border-slate-200 focus:border-indigo-500 focus:bg-white outline-none transition resize-y leading-relaxed"
          />
          <div className="absolute bottom-3 right-4 text-[11px] font-mono text-slate-400">
            {transcript.length} characters
          </div>
        </div>

        {errorMsg && (
          <div className="flex items-center gap-2 p-2.5 text-xs text-rose-700 bg-rose-50 border border-rose-200 rounded-lg">
            <AlertCircle className="w-4 h-4 shrink-0 text-rose-500" />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Live Processing Stage Visualization */}
        {isExtracting && (
          <div className="p-3.5 rounded-xl bg-indigo-50/60 border border-indigo-100 space-y-2 animate-fade-in">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-indigo-900 flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-indigo-600 animate-spin" />
                <span>Analyzing Meeting Intelligence...</span>
              </span>
              <span className="text-[11px] font-mono text-indigo-600 font-medium">
                Stage {Math.min(analysisStageIndex + 1, 8)} of 8
              </span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-1">
              {stagesList.map((stg, i) => {
                const isDone = i < analysisStageIndex;
                const isCurrent = i === analysisStageIndex;
                return (
                  <div key={i} className="flex items-center gap-1.5 text-[11px]">
                    {isDone ? (
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                    ) : isCurrent ? (
                      <Loader2 className="w-3.5 h-3.5 text-indigo-600 animate-spin shrink-0" />
                    ) : (
                      <span className="w-3.5 h-3.5 rounded-full border border-slate-300 shrink-0 inline-block"></span>
                    )}
                    <span className={`truncate ${isDone ? 'text-emerald-800 font-medium' : isCurrent ? 'text-indigo-900 font-semibold' : 'text-slate-400'}`}>
                      {stg}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        <div className="flex items-center justify-between pt-1">
          <div className="flex items-center gap-2 text-xs text-slate-500">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span>Real-Time WebSocket Agent Ready</span>
          </div>

          <button
            type="submit"
            disabled={isExtracting || !transcript.trim()}
            className={`flex items-center gap-2 px-5 py-2 rounded-lg font-semibold text-xs sm:text-sm text-white shadow-sm transition active:scale-95 ${
              isExtracting || !transcript.trim()
                ? 'bg-slate-300 text-slate-500 cursor-not-allowed border border-slate-300'
                : 'bg-indigo-600 hover:bg-indigo-700 border border-indigo-600'
            }`}
          >
            {isExtracting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin text-white" />
                <span>Running Agent...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-white" />
                <span>Run Agent Extraction</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
