import React from 'react';

export default function Navbar() {
  return (
    <header className="bg-white border-b border-slate-200 h-16 flex items-center justify-between px-6 shrink-0">
      <div className="flex items-center gap-4 md:hidden">
        <h2 className="text-xl font-bold text-indigo-600">MeetMind</h2>
      </div>
      <div className="flex-1"></div>
      <div className="flex items-center gap-4">
        <div className="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-600 font-bold">
          U
        </div>
      </div>
    </header>
  );
}
