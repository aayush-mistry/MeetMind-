import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMeeting } from '../context/MeetingContext';

export default function RecordAudio() {
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [duration, setDuration] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);
  
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  const timerRef = useRef(null);
  
  const { setMeetingId } = useMeeting();
  const navigate = useNavigate();

  const startRecording = async () => {
    console.log('[RecordAudio] startRecording clicked');
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      console.log('[RecordAudio] Microphone access granted');
      const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      mediaRecorder.onstop = handleStop;

      mediaRecorder.start();
      console.log('[RecordAudio] Recording started');
      setIsRecording(true);
      setIsPaused(false);
      
      timerRef.current = setInterval(() => {
        setDuration(prev => prev + 1);
      }, 1000);
    } catch (err) {
      console.error('[RecordAudio] Could not access microphone:', err);
      alert("Could not access microphone: " + err.message);
    }
  };

  const pauseRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.pause();
      setIsPaused(true);
      clearInterval(timerRef.current);
    }
  };

  const resumeRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'paused') {
      mediaRecorderRef.current.resume();
      setIsPaused(false);
      timerRef.current = setInterval(() => {
        setDuration(prev => prev + 1);
      }, 1000);
    }
  };

  const stopRecording = () => {
    console.log('[RecordAudio] stopRecording clicked (Stop & Process button)');
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
      setIsRecording(false);
      setIsPaused(false);
      clearInterval(timerRef.current);
    } else {
      console.warn('[RecordAudio] mediaRecorderRef.current is null!');
    }
  };

  const handleStop = async () => {
    console.log('[RecordAudio] handleStop triggered by mediaRecorder.onstop');
    setIsProcessing(true);
    
    if (chunksRef.current.length === 0) {
      console.error('[RecordAudio] No audio chunks recorded!');
      alert('Recording failed: No audio data captured.');
      setIsProcessing(false);
      return;
    }

    const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
    const file = new File([blob], 'browser_recording.webm', { type: 'audio/webm' });
    console.log(`[RecordAudio] Generated file Blob: ${file.size} bytes`);
    
    const form = new FormData();
    form.append('file', file);
    
    try {
      console.log('[RecordAudio] Sending POST request to /api/meeting/upload');
      const res = await fetch(`/api/meeting/upload`, {
        method: 'POST',
        body: form,
      });
      
      console.log(`[RecordAudio] Backend responded with status: ${res.status}`);
      if (!res.ok) {
        const text = await res.text();
        throw new Error(`Server returned ${res.status}: ${text}`);
      }
      
      const data = await res.json();
      console.log('[RecordAudio] Backend response data:', data);
      
      if (data.meeting_id) {
        console.log('[RecordAudio] Setting meetingId and navigating to /live');
        setMeetingId(data.meeting_id);
        navigate('/live');
      } else {
        throw new Error('No meeting_id returned from backend');
      }
    } catch (err) {
      console.error('[RecordAudio] Upload error:', err);
      alert(`Upload failed: ${err.message}`);
    } finally {
      setIsProcessing(false);
      setDuration(0);
    }
  };

  const formatTime = (secs) => {
    const m = Math.floor(secs / 60).toString().padStart(2, '0');
    const s = (secs % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-slate-800">Record Audio</h1>
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-8 text-center">
        
        <div className={`w-32 h-32 mx-auto rounded-full flex items-center justify-center border-4 mb-6 transition-all ${isRecording && !isPaused ? 'border-rose-500 bg-rose-50 animate-pulse' : 'border-slate-200 bg-slate-50'}`}>
          <div className="text-4xl font-mono text-slate-800">{formatTime(duration)}</div>
        </div>

        {isProcessing ? (
          <p className="text-indigo-600 font-medium animate-pulse">Processing Recording...</p>
        ) : (
          <div className="flex justify-center gap-4">
            {!isRecording ? (
              <button onClick={startRecording} className="px-8 py-3 bg-rose-600 text-white rounded-lg font-medium hover:bg-rose-700 shadow-sm shadow-rose-200">
                Start Recording
              </button>
            ) : (
              <>
                {isPaused ? (
                  <button onClick={resumeRecording} className="px-8 py-3 bg-emerald-600 text-white rounded-lg font-medium hover:bg-emerald-700">
                    Resume
                  </button>
                ) : (
                  <button onClick={pauseRecording} className="px-8 py-3 bg-amber-500 text-white rounded-lg font-medium hover:bg-amber-600">
                    Pause
                  </button>
                )}
                <button onClick={stopRecording} className="px-8 py-3 bg-slate-800 text-white rounded-lg font-medium hover:bg-slate-900">
                  Stop & Process
                </button>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
