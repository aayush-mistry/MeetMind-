import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMeeting } from '../context/MeetingContext';

export default function UploadRecording() {
  const [uploadFile, setUploadFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const { setMeetingId } = useMeeting();
  const navigate = useNavigate();

  const handleUploadRecording = async () => {
    if (!uploadFile) return;
    setIsUploading(true);
    const form = new FormData();
    form.append('file', uploadFile);
    try {
      const res = await fetch(`/api/meeting/upload`, {
        method: 'POST',
        body: form,
      });
      const data = await res.json();
      if (data.meeting_id) {
        setMeetingId(data.meeting_id);
        navigate('/live');
      }
    } catch (err) {
      alert(`Failed to upload recording: ${err.message || 'Server error'}`);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-slate-800">Upload Recording</h1>
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-8 text-center">
        <div className="w-16 h-16 bg-indigo-50 text-indigo-600 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" /></svg>
        </div>
        <h3 className="text-lg font-semibold text-slate-800 mb-2">Upload Audio or Video</h3>
        <p className="text-sm text-slate-500 mb-6">Supports MP3, WAV, MP4, WEBM, FLAC.</p>
        
        <input
          type="file"
          id="file-upload"
          accept="audio/*,video/*"
          onChange={e => setUploadFile(e.target.files[0])}
          className="hidden"
        />
        <label
          htmlFor="file-upload"
          className="inline-block px-6 py-3 bg-slate-50 border border-slate-300 rounded-lg font-medium text-slate-700 hover:bg-slate-100 cursor-pointer transition-colors shadow-sm mb-4"
        >
          {uploadFile ? uploadFile.name : 'Choose File'}
        </label>
        
        <div className="block mt-4">
          <button
            onClick={handleUploadRecording}
            disabled={!uploadFile || isUploading}
            className={`px-8 py-3 rounded-lg font-medium transition-all shadow-sm ${uploadFile && !isUploading ? 'bg-indigo-600 text-white hover:bg-indigo-700' : 'bg-slate-100 text-slate-400 cursor-not-allowed'}`}
          >
            {isUploading ? 'Uploading & Processing...' : 'Upload & Analyze'}
          </button>
        </div>
      </div>
    </div>
  );
}
