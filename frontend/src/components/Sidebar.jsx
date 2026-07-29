import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Radio, Mic, UploadCloud, History, MessageSquare, BarChart, Settings, Calendar, FileText, Hash, Search } from 'lucide-react';

export default function Sidebar() {
  const links = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'Live Meeting', path: '/live', icon: Radio },
    { name: 'Record Audio', path: '/record', icon: Mic },
    { name: 'Upload Recording', path: '/upload', icon: UploadCloud },
    { name: 'Meeting History', path: '/history', icon: History },
    { name: 'Semantic Search', path: '/search', icon: Search },
    { name: 'AI Chat', path: '/chat', icon: MessageSquare },
    { name: 'Analytics', path: '/analytics', icon: BarChart },
    { name: 'Settings', path: '/settings', icon: Settings },
    { name: 'Calendar', path: '/calendar', icon: Calendar },
    { name: 'Meeting Minutes', path: '/minutes', icon: FileText },
    { name: 'Topics', path: '/topics', icon: Hash },
  ];

  return (
    <aside className="w-64 bg-white border-r border-slate-200 hidden md:flex flex-col h-full shrink-0">
      <div className="p-4 border-b border-slate-200">
        <h2 className="text-xl font-bold text-indigo-600">MeetMind</h2>
      </div>
      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        {links.map((link) => (
          <NavLink
            key={link.name}
            to={link.path}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                isActive ? 'bg-indigo-50 text-indigo-600' : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
              }`
            }
          >
            <link.icon className="w-5 h-5" />
            {link.name}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
