import sqlite3
import json
import os
from typing import List, Optional, Dict, Any
from app.models import ActionItem, Decision, RiskBlocker, MeetingSummary, Meeting, AgentEvent, CalendarAccount, CalendarEvent, SpeakerMapping, MeetingMinute, ExportLog, MeetingTopic
DB_FILE = os.path.join(os.path.dirname(__file__), "..", "meeting_agent.db")

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Meetings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS meetings (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            transcript TEXT NOT NULL,
            created_at TEXT NOT NULL,
            meeting_type TEXT DEFAULT 'live',
            original_language TEXT,
            translation_language TEXT,
            file_name TEXT,
            file_size INTEGER,
            duration_seconds INTEGER,
            processing_time_seconds INTEGER
        )
    """)

    # Meeting Summaries table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS meeting_summaries (
            meeting_id TEXT PRIMARY KEY,
            summary_text TEXT NOT NULL,
            action_items_count INTEGER DEFAULT 0,
            decisions_count INTEGER DEFAULT 0,
            risks_count INTEGER DEFAULT 0,
            blockers_count INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)
    
    # Action items table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS action_items (
            id TEXT PRIMARY KEY,
            meeting_id TEXT NOT NULL,
            task_title TEXT NOT NULL,
            task_description TEXT,
            owner TEXT NOT NULL,
            deadline TEXT,
            priority TEXT NOT NULL,
            status TEXT NOT NULL,
            confidence REAL DEFAULT 0.90,
            source_quote TEXT,
            needs_review INTEGER DEFAULT 0,
            dependencies TEXT DEFAULT '[]',
            reminders_sent INTEGER DEFAULT 0,
            escalated INTEGER DEFAULT 0,
            escalated_to TEXT,
            last_reminder_at TEXT,
            created_at TEXT NOT NULL
        )
    """)
    
    # Decisions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS decisions (
            id TEXT PRIMARY KEY,
            meeting_id TEXT NOT NULL,
            decision TEXT NOT NULL,
            decided_by TEXT NOT NULL,
            source_quote TEXT,
            confidence REAL DEFAULT 0.95,
            created_at TEXT NOT NULL
        )
    """)

    # Risks & Blockers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS risks_blockers (
            id TEXT PRIMARY KEY,
            meeting_id TEXT NOT NULL,
            type TEXT NOT NULL,
            description TEXT NOT NULL,
            severity TEXT NOT NULL,
            blocked_task TEXT,
            depends_on TEXT,
            source_quote TEXT,
            confidence REAL DEFAULT 0.90,
            created_at TEXT NOT NULL
        )
    """)

    # Agent events table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agent_events (
            id TEXT PRIMARY KEY,
            meeting_id TEXT NOT NULL,
            type TEXT NOT NULL,
            action TEXT NOT NULL,
            reason TEXT NOT NULL,
            signals TEXT DEFAULT '[]',
            target TEXT,
            timestamp TEXT NOT NULL
        )
    """)
    
    # Calendar Accounts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS calendar_accounts (
            user_id TEXT NOT NULL,
            provider TEXT NOT NULL,
            access_token TEXT NOT NULL,
            refresh_token TEXT,
            created_at TEXT NOT NULL,
            PRIMARY KEY (user_id, provider)
        )
    """)

    # Calendar Events table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS calendar_events (
            id TEXT PRIMARY KEY,
            event_id TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            participants TEXT,
            platform TEXT,
            meeting_id TEXT,
            status TEXT,
            created_at TEXT NOT NULL
        )
    """)

    # Speaker Mappings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS speaker_mappings (
            meeting_id TEXT NOT NULL,
            original_speaker TEXT NOT NULL,
            mapped_speaker TEXT NOT NULL,
            PRIMARY KEY (meeting_id, original_speaker)
        )
    """)

    # Meeting Minutes table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS meeting_minutes (
            meeting_id TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            format TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # Meeting Topics table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS meeting_topics (
            id TEXT PRIMARY KEY,
            meeting_id TEXT NOT NULL,
            topic_name TEXT NOT NULL,
            start_time TEXT,
            end_time TEXT,
            duration TEXT,
            summary TEXT,
            keywords TEXT,
            speakers TEXT,
            confidence REAL DEFAULT 0.90,
            transcript_range TEXT,
            created_at TEXT NOT NULL
        )
    """)

    # Export Logs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS export_logs (
            id TEXT PRIMARY KEY,
            meeting_id TEXT NOT NULL,
            format TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    
    # Indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_action_items_meeting_id ON action_items(meeting_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_decisions_meeting_id ON decisions(meeting_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_risks_blockers_meeting_id ON risks_blockers(meeting_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_agent_events_meeting_id ON agent_events(meeting_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_meeting_topics_meeting_id ON meeting_topics(meeting_id)")
    
    conn.commit()
    conn.close()

# --- MEETINGS ---
def save_meeting(meeting: Meeting):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO meetings (id, title, description, transcript, created_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            title=excluded.title,
            description=excluded.description,
            transcript=excluded.transcript
    """, (meeting.id, meeting.title, meeting.description, meeting.transcript, meeting.created_at))
    conn.commit()
    conn.close()

def get_meetings() -> List[Meeting]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM meetings ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [Meeting(id=r["id"], title=r["title"], description=r["description"], transcript=r["transcript"], created_at=r["created_at"]) for r in rows]

def get_meeting(meeting_id: str) -> Optional[Meeting]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM meetings WHERE id = ?", (meeting_id,))
    r = cursor.fetchone()
    conn.close()
    if not r:
        return None
    return Meeting(id=r["id"], title=r["title"], description=r["description"], transcript=r["transcript"], created_at=r["created_at"])

# --- MEETING SUMMARY ---
def save_meeting_summary(summary: MeetingSummary):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO meeting_summaries (meeting_id, summary_text, action_items_count, decisions_count, risks_count, blockers_count, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(meeting_id) DO UPDATE SET
            summary_text=excluded.summary_text,
            action_items_count=excluded.action_items_count,
            decisions_count=excluded.decisions_count,
            risks_count=excluded.risks_count,
            blockers_count=excluded.blockers_count
    """, (summary.meeting_id, summary.summary_text, summary.action_items_count, summary.decisions_count, summary.risks_count, summary.blockers_count, summary.created_at))
    conn.commit()
    conn.close()

def get_meeting_summary(meeting_id: str) -> Optional[MeetingSummary]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM meeting_summaries WHERE meeting_id = ?", (meeting_id,))
    r = cursor.fetchone()
    conn.close()
    if not r:
        return None
    return MeetingSummary(
        meeting_id=r["meeting_id"],
        summary_text=r["summary_text"],
        action_items_count=r["action_items_count"],
        decisions_count=r["decisions_count"],
        risks_count=r["risks_count"],
        blockers_count=r["blockers_count"],
        created_at=r["created_at"]
    )

# --- TOPICS ---
def save_topic(topic: MeetingTopic):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO meeting_topics (id, meeting_id, topic_name, start_time, end_time, duration, summary, keywords, speakers, confidence, transcript_range, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            topic_name=excluded.topic_name,
            start_time=excluded.start_time,
            end_time=excluded.end_time,
            duration=excluded.duration,
            summary=excluded.summary,
            keywords=excluded.keywords,
            speakers=excluded.speakers,
            confidence=excluded.confidence,
            transcript_range=excluded.transcript_range
    """, (topic.id, topic.meeting_id, topic.topic_name, topic.start_time, topic.end_time, topic.duration, topic.summary, json.dumps(topic.keywords), json.dumps(topic.speakers), topic.confidence, topic.transcript_range, topic.created_at))
    conn.commit()
    conn.close()

def get_topics(meeting_id: str) -> List[MeetingTopic]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM meeting_topics WHERE meeting_id = ? ORDER BY created_at ASC", (meeting_id,))
    rows = cursor.fetchall()
    conn.close()
    topics = []
    for r in rows:
        keywords = []
        speakers = []
        try:
            keywords = json.loads(r["keywords"])
            speakers = json.loads(r["speakers"])
        except:
            pass
        topics.append(MeetingTopic(
            id=r["id"], meeting_id=r["meeting_id"], topic_name=r["topic_name"],
            start_time=r["start_time"], end_time=r["end_time"], duration=r["duration"],
            summary=r["summary"], keywords=keywords, speakers=speakers, confidence=r["confidence"],
            transcript_range=r["transcript_range"], created_at=r["created_at"]
        ))
    return topics

def delete_topics(meeting_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM meeting_topics WHERE meeting_id = ?", (meeting_id,))
    conn.commit()
    conn.close()

# --- ACTION ITEMS ---
def save_action_item(item: ActionItem):
    conn = get_db_connection()
    cursor = conn.cursor()
    deps_json = json.dumps(item.dependencies)
    cursor.execute("""
        INSERT INTO action_items (
            id, meeting_id, task_title, task_description, owner, deadline, priority, status,
            confidence, source_quote, needs_review, dependencies, reminders_sent, escalated, escalated_to, last_reminder_at, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            task_title=excluded.task_title,
            task_description=excluded.task_description,
            owner=excluded.owner,
            deadline=excluded.deadline,
            priority=excluded.priority,
            status=excluded.status,
            confidence=excluded.confidence,
            source_quote=excluded.source_quote,
            needs_review=excluded.needs_review,
            dependencies=excluded.dependencies,
            reminders_sent=excluded.reminders_sent,
            escalated=excluded.escalated,
            escalated_to=excluded.escalated_to,
            last_reminder_at=excluded.last_reminder_at
    """, (
        item.id, item.meeting_id, item.task_title, item.task_description, item.owner,
        item.deadline, item.priority, item.status, item.confidence, item.source_quote,
        1 if item.needs_review else 0, deps_json, item.reminders_sent,
        1 if item.escalated else 0, item.escalated_to, item.last_reminder_at, item.created_at
    ))
    conn.commit()
    conn.close()

def get_action_items(meeting_id: str) -> List[ActionItem]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM action_items WHERE meeting_id = ? ORDER BY created_at ASC", (meeting_id,))
    rows = cursor.fetchall()
    conn.close()
    
    items = []
    for r in rows:
        deps = []
        try:
            deps = json.loads(r["dependencies"]) if r["dependencies"] else []
        except Exception:
            deps = []

        items.append(ActionItem(
            id=r["id"],
            meeting_id=r["meeting_id"],
            task_title=r["task_title"],
            task_description=r["task_description"] or "",
            owner=r["owner"],
            deadline=r["deadline"],
            priority=r["priority"],
            status=r["status"],
            confidence=r["confidence"],
            source_quote=r["source_quote"] or "",
            needs_review=bool(r["needs_review"]),
            dependencies=deps,
            reminders_sent=r["reminders_sent"],
            escalated=bool(r["escalated"]),
            escalated_to=r["escalated_to"],
            last_reminder_at=r["last_reminder_at"],
            created_at=r["created_at"]
        ))
    return items

def get_action_item_by_id(meeting_id: str, item_id: str) -> Optional[ActionItem]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM action_items WHERE meeting_id = ? AND id = ?", (meeting_id, item_id))
    r = cursor.fetchone()
    conn.close()
    if not r:
        return None
    deps = []
    try:
        deps = json.loads(r["dependencies"]) if r["dependencies"] else []
    except Exception:
        deps = []

    return ActionItem(
        id=r["id"],
        meeting_id=r["meeting_id"],
        task_title=r["task_title"],
        task_description=r["task_description"] or "",
        owner=r["owner"],
        deadline=r["deadline"],
        priority=r["priority"],
        status=r["status"],
        confidence=r["confidence"],
        source_quote=r["source_quote"] or "",
        needs_review=bool(r["needs_review"]),
        dependencies=deps,
        reminders_sent=r["reminders_sent"],
        escalated=bool(r["escalated"]),
        escalated_to=r["escalated_to"],
        last_reminder_at=r["last_reminder_at"],
        created_at=r["created_at"]
    )

# --- DECISIONS ---
def save_decision(decision: Decision):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO decisions (id, meeting_id, decision, decided_by, source_quote, confidence, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (decision.id, decision.meeting_id, decision.decision, decision.decided_by, decision.source_quote, decision.confidence, decision.created_at))
    conn.commit()
    conn.close()

def get_decisions(meeting_id: str) -> List[Decision]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM decisions WHERE meeting_id = ? ORDER BY created_at ASC", (meeting_id,))
    rows = cursor.fetchall()
    conn.close()
    return [Decision(id=r["id"], meeting_id=r["meeting_id"], decision=r["decision"], decided_by=r["decided_by"], source_quote=r["source_quote"] or "", confidence=r["confidence"], created_at=r["created_at"]) for r in rows]

# --- RISKS & BLOCKERS ---
def save_risk_blocker(item: RiskBlocker):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO risks_blockers (id, meeting_id, type, description, severity, blocked_task, depends_on, source_quote, confidence, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (item.id, item.meeting_id, item.type, item.description, item.severity, item.blocked_task, item.depends_on, item.source_quote, item.confidence, item.created_at))
    conn.commit()
    conn.close()

def get_risks_blockers(meeting_id: str) -> List[RiskBlocker]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM risks_blockers WHERE meeting_id = ? ORDER BY created_at ASC", (meeting_id,))
    rows = cursor.fetchall()
    conn.close()
    return [RiskBlocker(
        id=r["id"],
        meeting_id=r["meeting_id"],
        type=r["type"],
        description=r["description"],
        severity=r["severity"],
        blocked_task=r["blocked_task"],
        depends_on=r["depends_on"],
        source_quote=r["source_quote"] or "",
        confidence=r["confidence"],
        created_at=r["created_at"]
    ) for r in rows]

# --- AGENT EVENTS ---
def save_agent_event(event: AgentEvent):
    conn = get_db_connection()
    cursor = conn.cursor()
    signals_json = json.dumps(event.signals)
    cursor.execute("""
        INSERT INTO agent_events (id, meeting_id, type, action, reason, signals, target, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (event.id, event.meeting_id, event.type, event.action, event.reason, signals_json, event.target, event.timestamp))
    conn.commit()
    conn.close()

def get_agent_events(meeting_id: str) -> List[AgentEvent]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM agent_events WHERE meeting_id = ? ORDER BY timestamp DESC", (meeting_id,))
    rows = cursor.fetchall()
    conn.close()
    events = []
    for r in rows:
        sigs = []
        try:
            sigs = json.loads(r["signals"]) if r["signals"] else []
        except Exception:
            sigs = []
        events.append(AgentEvent(
            id=r["id"],
            meeting_id=r["meeting_id"],
            type=r["type"],
            action=r["action"],
            reason=r["reason"],
            signals=sigs,
            target=r["target"] or "",
            timestamp=r["timestamp"]
        ))
    return events

def clear_meeting_data(meeting_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM action_items WHERE meeting_id = ?", (meeting_id,))
    cursor.execute("DELETE FROM decisions WHERE meeting_id = ?", (meeting_id,))
    cursor.execute("DELETE FROM risks_blockers WHERE meeting_id = ?", (meeting_id,))
    cursor.execute("DELETE FROM agent_events WHERE meeting_id = ?", (meeting_id,))
    cursor.execute("DELETE FROM meeting_summaries WHERE meeting_id = ?", (meeting_id,))
    cursor.execute("DELETE FROM meeting_topics WHERE meeting_id = ?", (meeting_id,))
    cursor.execute("DELETE FROM meetings WHERE id = ?", (meeting_id,))
    cursor.execute("DELETE FROM speaker_mappings WHERE meeting_id = ?", (meeting_id,))
    cursor.execute("DELETE FROM meeting_minutes WHERE meeting_id = ?", (meeting_id,))
    conn.commit()
    conn.close()

# --- CALENDAR ACCOUNTS ---
def save_calendar_account(account: CalendarAccount):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO calendar_accounts (user_id, provider, access_token, refresh_token, created_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(user_id, provider) DO UPDATE SET
            access_token=excluded.access_token,
            refresh_token=excluded.refresh_token
    """, (account.user_id, account.provider, account.access_token, account.refresh_token, account.created_at))
    conn.commit()
    conn.close()

def get_calendar_account(user_id: str, provider: str) -> Optional[CalendarAccount]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM calendar_accounts WHERE user_id = ? AND provider = ?", (user_id, provider))
    r = cursor.fetchone()
    conn.close()
    if not r:
        return None
    return CalendarAccount(**dict(r))

def delete_calendar_account(user_id: str, provider: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM calendar_accounts WHERE user_id = ? AND provider = ?", (user_id, provider))
    conn.commit()
    conn.close()

# --- CALENDAR EVENTS ---
def save_calendar_event(event: CalendarEvent):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO calendar_events (id, event_id, title, start_time, end_time, participants, platform, meeting_id, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(event_id) DO UPDATE SET
            title=excluded.title,
            start_time=excluded.start_time,
            end_time=excluded.end_time,
            participants=excluded.participants,
            platform=excluded.platform,
            meeting_id=excluded.meeting_id,
            status=excluded.status
    """, (event.id, event.event_id, event.title, event.start_time, event.end_time, event.participants, event.platform, event.meeting_id, event.status, event.created_at))
    conn.commit()
    conn.close()

def get_calendar_events() -> List[CalendarEvent]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM calendar_events ORDER BY start_time ASC")
    rows = cursor.fetchall()
    conn.close()
    return [CalendarEvent(**dict(r)) for r in rows]

def link_calendar_event(event_id: str, meeting_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE calendar_events SET meeting_id = ? WHERE event_id = ?", (meeting_id, event_id))
    conn.commit()
    conn.close()

# --- SPEAKER MAPPINGS ---
def save_speaker_mapping(mapping: SpeakerMapping):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO speaker_mappings (meeting_id, original_speaker, mapped_speaker)
        VALUES (?, ?, ?)
        ON CONFLICT(meeting_id, original_speaker) DO UPDATE SET
            mapped_speaker=excluded.mapped_speaker
    """, (mapping.meeting_id, mapping.original_speaker, mapping.mapped_speaker))
    conn.commit()
    conn.close()

def get_speaker_mappings(meeting_id: str) -> List[SpeakerMapping]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM speaker_mappings WHERE meeting_id = ?", (meeting_id,))
    rows = cursor.fetchall()
    conn.close()
    return [SpeakerMapping(**dict(r)) for r in rows]

# --- MEETING MINUTES ---
def save_meeting_minute(minute: MeetingMinute):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO meeting_minutes (meeting_id, content, format, created_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(meeting_id) DO UPDATE SET
            content=excluded.content,
            format=excluded.format
    """, (minute.meeting_id, minute.content, minute.format, minute.created_at))
    conn.commit()
    conn.close()

def get_meeting_minute(meeting_id: str) -> Optional[MeetingMinute]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM meeting_minutes WHERE meeting_id = ?", (meeting_id,))
    r = cursor.fetchone()
    conn.close()
    if not r:
        return None
    return MeetingMinute(**dict(r))

# --- EXPORT LOGS ---
def log_export(export: ExportLog):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO export_logs (id, meeting_id, format, timestamp)
        VALUES (?, ?, ?, ?)
    """, (export.id, export.meeting_id, export.format, export.timestamp))
    conn.commit()
    conn.close()
