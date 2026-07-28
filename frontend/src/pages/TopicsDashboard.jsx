import React, { useEffect, useState } from 'react';
import { useMeeting } from '../context/MeetingContext';
import { Search, Hash, Clock, List, Filter } from 'lucide-react';

export default function TopicsDashboard() {
  const { meetingId } = useMeeting();
  const [topics, setTopics] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTopics = async () => {
      setLoading(true);
      try {
        const res = await fetch('http://localhost:8000/api/meeting/' + meetingId);
        const data = await res.json();
        if (data && data.topics) {
          setTopics(data.topics);
        } else {
          setTopics([]);
        }
      } catch (err) {
        console.error(err);
      }
      setLoading(false);
    };
    fetchTopics();
  }, [meetingId]);

  const filteredTopics = topics.filter(t => 
    t.topic_name.toLowerCase().includes(searchQuery.toLowerCase()) || 
    (t.keywords && t.keywords.some(k => k.toLowerCase().includes(searchQuery.toLowerCase())))
  );

  const totalTopics = topics.length;
  const avgDuration = topics.length ? (topics.reduce((acc, t) => acc + (parseInt(t.duration) || 5), 0) / topics.length).toFixed(1) : 0;

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <Hash className="w-6 h-6 text-indigo-600" />
            Meeting Topics
          </h1>
          <p className="text-slate-500 mt-1">AI-detected discussion themes and timelines</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <div className="text-sm font-medium text-slate-500 uppercase">Topics Discussed</div>
          <div className="text-3xl font-bold text-slate-900 mt-2">{totalTopics}</div>
        </div>
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <div className="text-sm font-medium text-slate-500 uppercase">Avg. Topic Length</div>
          <div className="text-3xl font-bold text-slate-900 mt-2">{avgDuration} min</div>
        </div>
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <div className="text-sm font-medium text-slate-500 uppercase">Active Meeting</div>
          <div className="text-lg font-semibold text-slate-900 mt-2 truncate">{meetingId}</div>
        </div>
      </div>

      <div className="flex gap-4 items-center bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
        <div className="relative flex-1">
          <Search className="w-5 h-5 absolute left-3 top-3 text-slate-400" />
          <input 
            type="text"
            placeholder="Search topics by name or keywords..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12 text-slate-500">Loading topics...</div>
      ) : filteredTopics.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-xl border border-slate-200 shadow-sm">
          <Hash className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <p className="text-slate-500">No topics found for this meeting.</p>
        </div>
      ) : (
        <div className="space-y-6 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-slate-300 before:to-transparent">
          {filteredTopics.map((topic, index) => (
            <div key={topic.id} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
              <div className="flex items-center justify-center w-10 h-10 rounded-full border border-white bg-indigo-100 text-indigo-600 shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 shadow-sm z-10 font-bold">
                {index + 1}
              </div>
              
              <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] bg-white p-5 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow cursor-pointer">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-bold text-slate-900 text-lg">{topic.topic_name}</h3>
                  <span className="text-xs font-medium bg-slate-100 text-slate-600 px-2 py-1 rounded-full flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {topic.start_time} {topic.end_time ? '- ' + topic.end_time : ''}
                  </span>
                </div>
                
                <p className="text-slate-600 text-sm mb-4 leading-relaxed">{topic.summary}</p>
                
                <div className="flex flex-wrap gap-2 mb-3">
                  {topic.keywords?.map(kw => (
                    <span key={kw} className="text-xs font-medium bg-indigo-50 text-indigo-600 px-2.5 py-1 rounded-md">
                      {kw}
                    </span>
                  ))}
                </div>

                <div className="flex items-center justify-between border-t border-slate-100 pt-3 mt-3">
                  <div className="text-xs text-slate-500">
                    <span className="font-medium text-slate-700">Duration:</span> {topic.duration}
                  </div>
                  <div className="text-xs text-slate-500 flex items-center gap-1">
                    <span className="w-2 h-2 rounded-full bg-green-500"></span>
                    Conf: {(topic.confidence * 100).toFixed(0)}%
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
