import React, { createContext, useState, useEffect, useRef, useContext } from 'react';

const API_BASE = `/api`;
const WS_BASE = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws`;

export const MeetingContext = createContext();

export const useMeeting = () => useContext(MeetingContext);

export const MeetingProvider = ({ children }) => {
  const [meetingId, setMeetingId] = useState('demo_meeting');
  
  const [summary, setSummary] = useState(null);
  const [items, setItems] = useState([]);
  const [decisions, setDecisions] = useState([]);
  const [risksBlockers, setRisksBlockers] = useState([]);
  const [agentEvents, setAgentEvents] = useState([]);

  const [wsConnected, setWsConnected] = useState(false);
  const [isExtracting, setIsExtracting] = useState(false);
  const [analysisStageIndex, setAnalysisStageIndex] = useState(-1);

  const wsRef = useRef(null);

  const fetchMeetingData = (mId) => {
    fetch(`${API_BASE}/meeting/${mId}`)
      .then(res => res.json())
      .then(data => {
        if (data.summary) setSummary(data.summary);
        if (Array.isArray(data.action_items)) setItems(data.action_items);
        if (Array.isArray(data.decisions)) setDecisions(data.decisions);
        if (Array.isArray(data.risks_blockers)) setRisksBlockers(data.risks_blockers);
        if (Array.isArray(data.events)) setAgentEvents(data.events);
      })
      .catch(err => console.log('Fetch meeting data error:', err));
  };

  useEffect(() => {
    fetchMeetingData(meetingId);
  }, [meetingId]);

  useEffect(() => {
    let ws = null;
    let reconnectTimeout = null;

    const connectWebSocket = () => {
      ws = new WebSocket(`${WS_BASE}/meeting/${meetingId}`);
      wsRef.current = ws;

      ws.onopen = () => {
        setWsConnected(true);
        console.log(`[WebSocket] Agent connected to meeting '${meetingId}'`);
      };

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          switch (msg.type) {
            case 'processing_started':
              setIsExtracting(true);
              setAnalysisStageIndex(0);
              break;
            case 'analysis_stage':
              if (typeof msg.stage_index === 'number') {
                setAnalysisStageIndex(msg.stage_index);
              }
              break;
            case 'summary_extracted':
              if (msg.data) setSummary(msg.data);
              break;
            case 'decision_extracted':
              if (msg.data && msg.data.id) {
                setDecisions(prev => [msg.data, ...prev]);
              }
              break;
            case 'risk_extracted':
              if (msg.data && msg.data.id) {
                setRisksBlockers(prev => [msg.data, ...prev]);
              }
              break;
            case 'item_extracted':
              if (msg.data && msg.data.id) {
                setItems(prev => {
                  const exists = prev.some(item => item.id === msg.data.id);
                  if (exists) {
                    return prev.map(item => item.id === msg.data.id ? msg.data : item);
                  }
                  return [...prev, msg.data];
                });
              }
              break;
            case 'processing_complete':
              setIsExtracting(false);
              setAnalysisStageIndex(7);
              break;
            case 'reminder_sent':
              if (msg.data) {
                setItems(prev => prev.map(item => {
                  if (item.id === msg.data.id) {
                    return { ...item, status: 'reminded', reminders_sent: msg.data.reminders_sent };
                  }
                  return item;
                }));
                setAgentEvents(prev => [{
                  id: `evt_${Date.now()}`,
                  meeting_id: meetingId,
                  type: 'reminder_sent',
                  action: 'SEND_REMINDER',
                  reason: msg.data.reason || 'Deadline approaching for task.',
                  signals: msg.data.signals || [],
                  target: `@${msg.data.owner}`,
                  timestamp: msg.data.timestamp || new Date().toISOString()
                }, ...prev]);
              }
              break;
            case 'item_escalated':
              if (msg.data && msg.data.item) {
                setItems(prev => prev.map(item => item.id === msg.data.item.id ? msg.data.item : item));
                if (msg.data.event) {
                  setAgentEvents(prev => [msg.data.event, ...prev]);
                }
              }
              break;
            case 'item_updated':
              if (msg.data && msg.data.id) {
                setItems(prev => prev.map(item => item.id === msg.data.id ? msg.data : item));
              }
              break;
            case 'item_completed':
              if (msg.data && msg.data.id) {
                setItems(prev => prev.map(item => item.id === msg.data.id ? { ...item, status: 'completed' } : item));
              }
              break;
            case 'agent_event':
              if (msg.data) {
                setAgentEvents(prev => [msg.data, ...prev]);
              }
              break;
            case 'meeting_reset':
              setSummary(null);
              setItems([]);
              setDecisions([]);
              setRisksBlockers([]);
              setAgentEvents([]);
              setIsExtracting(false);
              setAnalysisStageIndex(-1);
              break;
            default:
              break;
          }
        } catch (err) {
          console.error('[WebSocket] Event parse error:', err);
        }
      };

      ws.onclose = () => {
        setWsConnected(false);
        reconnectTimeout = setTimeout(connectWebSocket, 3000);
      };

      ws.onerror = (err) => {
        console.error('[WebSocket] Error:', err);
        ws.close();
      };
    };

    connectWebSocket();

    return () => {
      if (reconnectTimeout) clearTimeout(reconnectTimeout);
      if (ws) {
        ws.onclose = null;
        ws.onerror = null;
        ws.close();
      }
    };
  }, [meetingId]);

  return (
    <MeetingContext.Provider value={{
      meetingId,
      setMeetingId,
      summary,
      setSummary,
      items,
      setItems,
      decisions,
      setDecisions,
      risksBlockers,
      setRisksBlockers,
      agentEvents,
      setAgentEvents,
      wsConnected,
      isExtracting,
      setIsExtracting,
      analysisStageIndex,
      setAnalysisStageIndex,
      wsRef
    }}>
      {children}
    </MeetingContext.Provider>
  );
};
