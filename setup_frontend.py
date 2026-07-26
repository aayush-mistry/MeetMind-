import os

base_dir = r"d:\MeetMind--main\frontend\src"

dirs_to_create = [
    "components",
    "pages",
]

for d in dirs_to_create:
    os.makedirs(os.path.join(base_dir, d), exist_ok=True)

files = {
    "components/Sidebar.jsx": """import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Radio, Mic, UploadCloud, History, MessageSquare, BarChart, Settings } from 'lucide-react';

export default function Sidebar() {
  const links = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'Live Meeting', path: '/live', icon: Radio },
    { name: 'Record Audio', path: '/record', icon: Mic },
    { name: 'Upload Recording', path: '/upload', icon: UploadCloud },
    { name: 'Meeting History', path: '/history', icon: History },
    { name: 'AI Chat', path: '/chat', icon: MessageSquare },
    { name: 'Analytics', path: '/analytics', icon: BarChart },
    { name: 'Settings', path: '/settings', icon: Settings },
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
""",
    "components/Navbar.jsx": """import React from 'react';

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
""",
    "components/Layout.jsx": """import React from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Navbar from './Navbar';

export default function Layout() {
  return (
    <div className="flex h-screen overflow-hidden bg-slate-50 text-slate-900">
      <Sidebar />
      <div className="flex flex-col flex-1 min-w-0">
        <Navbar />
        <main className="flex-1 overflow-y-auto p-4 md:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
""",
    "pages/Dashboard.jsx": """import React from 'react';

export default function Dashboard() {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Dashboard</h1>
      <p>Welcome to MeetMind Dashboard.</p>
    </div>
  );
}
""",
    "pages/LiveMeeting.jsx": """import React from 'react';
import { useMeeting } from '../context/MeetingContext';

export default function LiveMeeting() {
  const { meetingId } = useMeeting();
  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Live Meeting</h1>
      <p>Current Meeting: {meetingId}</p>
    </div>
  );
}
""",
    "pages/RecordAudio.jsx": """import React from 'react';

export default function RecordAudio() {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Record Audio</h1>
      <p>Record your meeting directly in the browser.</p>
    </div>
  );
}
""",
    "pages/UploadRecording.jsx": """import React from 'react';

export default function UploadRecording() {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Upload Recording</h1>
      <p>Upload a past recording for AI processing.</p>
    </div>
  );
}
""",
    "pages/MeetingHistory.jsx": """import React from 'react';

export default function MeetingHistory() {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Meeting History</h1>
      <p>View your past meetings.</p>
    </div>
  );
}
""",
    "pages/AiChat.jsx": """import React from 'react';

export default function AiChat() {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">AI Chat</h1>
      <p>Ask questions about your past meetings.</p>
    </div>
  );
}
""",
    "pages/Analytics.jsx": """import React from 'react';

export default function Analytics() {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Analytics</h1>
      <p>View metrics for your meetings.</p>
    </div>
  );
}
""",
    "pages/Settings.jsx": """import React from 'react';

export default function Settings() {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Settings</h1>
      <p>Configure your preferences.</p>
    </div>
  );
}
"""
}

for path, content in files.items():
    full_path = os.path.join(base_dir, path)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Setup completed.")
