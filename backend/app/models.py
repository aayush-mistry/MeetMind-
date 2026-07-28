from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime


class ActionItem(BaseModel):
    id: str
    meeting_id: str
    task_title: str
    task_description: str = ""
    owner: str = "Unassigned"
    deadline: Optional[str] = None
    priority: Literal["low", "medium", "high", "critical"] = "medium"
    status: Literal[
        "pending",
        "due_soon",
        "reminded",
        "overdue",
        "needs_review",
        "at_risk",
        "completed",
    ] = "pending"
    confidence: float = 0.90
    source_quote: str = ""
    needs_review: bool = False
    dependencies: List[str] = Field(default_factory=list)
    reminders_sent: int = 0
    escalated: bool = False
    escalated_to: Optional[str] = None
    last_reminder_at: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class ActionItemCreate(BaseModel):
    task_title: str
    task_description: Optional[str] = ""
    owner: Optional[str] = "Unassigned"
    deadline: Optional[str] = None
    priority: Optional[Literal["low", "medium", "high", "critical"]] = "medium"


class ActionItemUpdate(BaseModel):
    task_title: Optional[str] = None
    task_description: Optional[str] = None
    owner: Optional[str] = None
    deadline: Optional[str] = None
    priority: Optional[Literal["low", "medium", "high", "critical"]] = None
    status: Optional[
        Literal[
            "pending",
            "due_soon",
            "reminded",
            "overdue",
            "needs_review",
            "at_risk",
            "completed",
        ]
    ] = None
    needs_review: Optional[bool] = None


class Decision(BaseModel):
    id: str
    meeting_id: str
    decision: str
    decided_by: str = "Team"
    source_quote: str = ""
    confidence: float = 0.95
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class RiskBlocker(BaseModel):
    id: str
    meeting_id: str
    type: Literal["risk", "blocker"] = "risk"
    description: str
    severity: Literal["low", "medium", "high", "critical"] = "medium"
    blocked_task: Optional[str] = None
    depends_on: Optional[str] = None
    source_quote: str = ""
    confidence: float = 0.90
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class MeetingSummary(BaseModel):
    meeting_id: str
    summary_text: str
    action_items_count: int = 0
    decisions_count: int = 0
    risks_count: int = 0
    blockers_count: int = 0
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class Meeting(BaseModel):
    id: str
    title: str
    description: Optional[str] = ""
    transcript: str
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class MeetingTopic(BaseModel):
    id: str
    meeting_id: str
    topic_name: str
    start_time: str = ""
    end_time: str = ""
    duration: str = ""
    summary: str = ""
    keywords: List[str] = Field(default_factory=list)
    speakers: List[str] = Field(default_factory=list)
    confidence: float = 0.90
    transcript_range: str = ""
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class TranscriptSubmission(BaseModel):
    text: str


class AgentEvent(BaseModel):
    id: str
    meeting_id: str
    type: str
    action: str
    reason: str
    signals: List[str] = Field(default_factory=list)
    target: str = ""
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


class CalendarAccount(BaseModel):
    user_id: str
    provider: Literal["google", "outlook"]
    access_token: str
    refresh_token: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class CalendarEvent(BaseModel):
    id: str
    event_id: str
    title: str
    start_time: str
    end_time: str
    participants: str = ""
    platform: str = "Offline"
    meeting_id: Optional[str] = None
    status: str = "scheduled"
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class SpeakerMapping(BaseModel):
    meeting_id: str
    original_speaker: str
    mapped_speaker: str


class MeetingMinute(BaseModel):
    meeting_id: str
    content: str
    format: str = "json"
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class ExportLog(BaseModel):
    id: str
    meeting_id: str
    format: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
