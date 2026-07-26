import React from 'react';

export default function Settings() {
  return (
    <div className="max-w-2xl space-y-6">
      <h1 className="text-2xl font-bold text-slate-800">Settings</h1>
      
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 divide-y divide-slate-100">
        <div className="p-6 flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-slate-800">Dark Mode</h3>
            <p className="text-sm text-slate-500">Toggle system theme.</p>
          </div>
          <button className="w-12 h-6 bg-slate-200 rounded-full relative transition-colors">
            <div className="w-5 h-5 bg-white rounded-full absolute top-0.5 left-0.5 shadow-sm"></div>
          </button>
        </div>
        
        <div className="p-6 flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-slate-800">Default Language</h3>
            <p className="text-sm text-slate-500">Set primary recording language.</p>
          </div>
          <select className="border border-slate-300 rounded-md px-3 py-1.5 text-sm">
            <option>English</option>
            <option>Spanish</option>
            <option>French</option>
          </select>
        </div>
        
        <div className="p-6 flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-slate-800">AI Notifications</h3>
            <p className="text-sm text-slate-500">Receive reminders for pending action items.</p>
          </div>
          <button className="w-12 h-6 bg-indigo-600 rounded-full relative transition-colors">
            <div className="w-5 h-5 bg-white rounded-full absolute top-0.5 right-0.5 shadow-sm"></div>
          </button>
        </div>
      </div>
    </div>
  );
}
