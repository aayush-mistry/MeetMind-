import React from 'react';

export default function Analytics() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-800">Analytics</h1>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-6 bg-white rounded-xl shadow-sm border border-slate-200">
          <p className="text-sm text-slate-500 font-medium">Total Meetings</p>
          <p className="text-3xl font-bold text-slate-800 mt-2">24</p>
        </div>
        <div className="p-6 bg-white rounded-xl shadow-sm border border-slate-200">
          <p className="text-sm text-slate-500 font-medium">Recording Time</p>
          <p className="text-3xl font-bold text-slate-800 mt-2">12.5 hrs</p>
        </div>
        <div className="p-6 bg-white rounded-xl shadow-sm border border-slate-200">
          <p className="text-sm text-slate-500 font-medium">Languages</p>
          <p className="text-3xl font-bold text-slate-800 mt-2">3</p>
        </div>
        <div className="p-6 bg-white rounded-xl shadow-sm border border-slate-200">
          <p className="text-sm text-slate-500 font-medium">Action Items</p>
          <p className="text-3xl font-bold text-slate-800 mt-2">142</p>
        </div>
      </div>
      <div className="p-8 bg-white rounded-xl shadow-sm border border-slate-200 flex items-center justify-center h-64">
        <p className="text-slate-500">Charts placeholder (Chart.js / Recharts integration)</p>
      </div>
    </div>
  );
}
