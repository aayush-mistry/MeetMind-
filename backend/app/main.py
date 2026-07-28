import asyncio
import json
import uuid
from typing import Dict, List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, File, UploadFile, BackgroundTasks, Form
from fastapi.middleware.cors import CORSMiddleware
from starlette.concurrency import run_in_threadpool
from datetime import datetime
import os
import shutil
import subprocess
from dotenv import load_dotenv

load_dotenv()
# Directory for uploaded recordings
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

from app import database, extractor, scheduler
from app.models import (
    ActionItem, ActionItemCreate, ActionItemUpdate, Decision, RiskBlocker, 
    MeetingSummary, Meeting, TranscriptSubmission, AgentEvent
)
from pydantic import BaseModel

class MeetingInit(BaseModel):
    title: str
    description: Optional[str] = ""
from app.samples import SAMPLE_TRANSCRIPTS

app = FastAPI(
    title="AI Meeting & Follow-Up Agent — Agentic Intelligence API",
    description="Real-Time WebSocket Pipeline & Autonomous Agentic Decision Engine",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

connections: Dict[str, List[WebSocket]] = {}

@app.on_event("startup")
def startup_event():
    database.init_db()
    print("[Server Startup] Database & Agentic Pipeline Initialized.")

async def broadcast(meeting_id: str, message: dict):
    ws_list = connections.get(meeting_id, [])
    to_remove = []
    for ws in list(ws_list):
        try:
            await ws.send_text(json.dumps(message))
        except Exception:
            to_remove.append(ws)
    for ws in to_remove:
        if ws in ws_list:
            ws_list.remove(ws)

@app.websocket("/ws/meeting/{meeting_id}")
async def ws_endpoint(websocket: WebSocket, meeting_id: str):
    await websocket.accept()
    connections.setdefault(meeting_id, []).append(websocket)
    
    await websocket.send_text(json.dumps({
        "type": "connected",
        "meeting_id": meeting_id,
        "message": "Connected to Real-Time Agentic Pipeline"
    }))

    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
    except (WebSocketDisconnect, Exception):
        if meeting_id in connections and websocket in connections[meeting_id]:
            connections[meeting_id].remove(websocket)

@app.get("/api/sample-transcripts")
def get_sample_transcripts():
    return SAMPLE_TRANSCRIPTS

@app.get("/api/meetings")
def list_meetings():
    return database.get_meetings()

@app.post("/api/meeting/init")
async def init_meeting(payload: MeetingInit):
    meeting_id = str(uuid.uuid4())
    meeting = Meeting(
        id=meeting_id,
        title=payload.title,
        description=payload.description,
        transcript="", 
        created_at=datetime.utcnow().isoformat()
    )
    await run_in_threadpool(database.save_meeting, meeting)
    return {"meeting_id": meeting_id, "status": "initialized"}

@app.get("/api/meeting/{meeting_id}")
def get_meeting_full(meeting_id: str):
    m = database.get_meeting(meeting_id)
    summary = database.get_meeting_summary(meeting_id)
    items = database.get_action_items(meeting_id)
    decisions = database.get_decisions(meeting_id)
    risks_blockers = database.get_risks_blockers(meeting_id)
    events = database.get_agent_events(meeting_id)
    topics = database.get_topics(meeting_id)
    return {
        "meeting": m.dict() if m else None,
        "summary": summary.dict() if summary else None,
        "action_items": [i.dict() for i in items],
        "decisions": [d.dict() for d in decisions],
        "risks_blockers": [rb.dict() for rb in risks_blockers],
        "events": [e.dict() for e in events],
        "topics": [t.dict() for t in topics]
    }

@app.post("/api/transcript/{meeting_id}")
async def submit_transcript(meeting_id: str, payload: TranscriptSubmission):
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Transcript text cannot be empty.")
    
    # Save Meeting record
    title_match = text.split("\n")[0][:40] if text else "Meeting Transcript"
    title = f"Sync: {title_match}..."
    meeting = Meeting(id=meeting_id, title=title, transcript=text)
    await run_in_threadpool(database.save_meeting, meeting)

    asyncio.create_task(process_agentic_pipeline(meeting_id, text))
    return {"status": "processing_started", "meeting_id": meeting_id}



async def process_agentic_pipeline(meeting_id: str, text: str):
    """Async Agent Pipeline with Live Processing Stage Visualizations."""
    try:
        stages = [
            "Transcript received",
            "Detecting speakers & context",
            "Understanding discussion & compiling summary",
            "Extracting explicit decisions",
            "Resolving commitments & assigning owners",
            "Detecting risks & mapping dependencies",
            "Calculating AI confidence scores",
            "Finalizing results"
        ]

        await broadcast(meeting_id, {
            "type": "processing_started",
            "meeting_id": meeting_id,
            "stages": stages
        })

        for idx, stage in enumerate(stages[:4]):
            await broadcast(meeting_id, {
                "type": "analysis_stage",
                "stage_index": idx,
                "stage_text": stage
            })
            await asyncio.sleep(0.2)

        # Perform AI extraction
        summary, items, decisions, risks_blockers, topics = await extractor.extract_meeting_intelligence(meeting_id, text)
    
        # Save summary
        await run_in_threadpool(database.save_meeting_summary, summary)
        await broadcast(meeting_id, {
            "type": "summary_extracted",
            "data": summary.dict()
        })

        for idx, stage in enumerate(stages[4:6], start=4):
            await broadcast(meeting_id, {
                "type": "analysis_stage",
                "stage_index": idx,
                "stage_text": stage
            })
            await asyncio.sleep(0.2)

        # Save decisions
        for d in decisions:
            await run_in_threadpool(database.save_decision, d)
            await broadcast(meeting_id, {
                "type": "decision_extracted",
                "data": d.dict()
            })
            await asyncio.sleep(0.15)

        # Save risks & blockers
        for rb in risks_blockers:
            await run_in_threadpool(database.save_risk_blocker, rb)
            await broadcast(meeting_id, {
                "type": "risk_extracted",
                "data": rb.dict()
            })
            await asyncio.sleep(0.15)

        # Save Action Items line by line
        for item in items:
            await run_in_threadpool(database.save_action_item, item)
            await broadcast(meeting_id, {
                "type": "item_extracted",
                "data": item.dict()
            })
            await asyncio.sleep(0.25)

        # Save Topics line by line
        for t in topics:
            await run_in_threadpool(database.save_topic, t)
            await broadcast(meeting_id, {
                "type": "topic_extracted",
                "data": t.dict()
            })
            await asyncio.sleep(0.15)

        # Broadcast final stage
        await broadcast(meeting_id, {
            "type": "analysis_stage",
            "stage_index": 7,
            "stage_text": "Finalizing results"
        })
    
        await broadcast(meeting_id, {
            "type": "processing_complete",
            "total_items": len(items),
            "total_decisions": len(decisions),
            "total_risks": len(risks_blockers),
            "total_topics": len(topics),
            "meeting_id": meeting_id
        })
    
        # Start Autonomous Agent Loop
        scheduler.start_agent_loop(meeting_id, broadcast)
    except Exception as e:
        print(f"[Pipeline Error] {e}")
        await broadcast(meeting_id, {
            "type": "agent_event",
            "data": {
                "id": str(uuid.uuid4())[:8],
                "meeting_id": meeting_id,
                "type": "pipeline_error",
                "action": "HALT",
                "reason": f"Pipeline failed: {str(e)}",
                "signals": ["Exception caught"],
                "target": "System",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        })

async def process_uploaded_meeting(meeting_id: str, file_path: str, metadata: Dict):
    """Process an uploaded audio/video file.
    Handles extraction, transcription, translation, and AI analysis.
    Broadcasts stage updates over WebSocket.
    """
    async def stage_update(stage: str, progress: float = 0.0):
        await broadcast(meeting_id, {"type": "stage_update", "stage": stage, "progress": progress})

    await stage_update("Transcribing Audio with AI Provider", progress=0.1)
    
    try:
        from app.services.ai.provider_factory import get_ai_provider
        provider = get_ai_provider()
        
        await stage_update("Transcribing and Translating", progress=0.3)
        detected_lang, transcript = await provider.transcribe_and_translate(file_path)

    except Exception as e:
        print(f"[Audio Processing] Transcription failed: {e}")
        detected_lang = "en"
        transcript = f"Transcription failed due to API error: {str(e)}"

    await stage_update(f"Language Detected: {detected_lang}", progress=0.6)
    
    # Save meeting record
    from app.models import Meeting
    meeting = Meeting(
        id=meeting_id, 
        title=metadata.get("file_name", "Uploaded Recording"), 
        description="Uploaded recording", 
        transcript=transcript, 
        created_at=datetime.utcnow().isoformat()
    )
    await run_in_threadpool(database.save_meeting, meeting)
    
    # Update metadata fields in DB
    conn = database.get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """UPDATE meetings SET meeting_type=?, original_language=?, translation_language=?, file_name=?, file_size=?, processing_time_seconds=? WHERE id=?""",
        (
            metadata.get("meeting_type"),
            detected_lang,
            "en",
            metadata.get("file_name"),
            metadata.get("file_size"),
            int(datetime.utcnow().timestamp() - datetime.fromisoformat(meeting.created_at).timestamp()),
            meeting_id,
        ),
    )
    conn.commit()
    conn.close()

    await stage_update("Generating AI Summary", progress=0.8)
    await process_agentic_pipeline(meeting_id, transcript)
    await stage_update("Completed", progress=1.0)

    # Cleanup local file
    if os.path.exists(file_path):
        os.remove(file_path)

@app.post("/api/meeting/{meeting_id}/items")
async def create_manual_item(meeting_id: str, payload: ActionItemCreate):
    item_id = f"item_{str(uuid.uuid4())[:6]}"
    item = ActionItem(
        id=item_id,
        meeting_id=meeting_id,
        task_title=payload.task_title,
        task_description=payload.task_description or "",
        owner=payload.owner or "Unassigned",
        deadline=payload.deadline,
        priority=payload.priority or "medium",
        status="pending",
        confidence=1.0,
        source_quote="Manually created item",
        needs_review=False
    )
    await run_in_threadpool(database.save_action_item, item)
    
    await broadcast(meeting_id, {
        "type": "item_extracted",
        "data": item.dict()
    })
    
    scheduler.start_agent_loop(meeting_id, broadcast)
    return item

@app.patch("/api/meeting/{meeting_id}/items/{item_id}")
async def update_item(meeting_id: str, item_id: str, payload: ActionItemUpdate):
    item = database.get_action_item_by_id(meeting_id, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if payload.task_title is not None:
        item.task_title = payload.task_title
    if payload.task_description is not None:
        item.task_description = payload.task_description
    if payload.owner is not None:
        item.owner = payload.owner
    if payload.deadline is not None:
        item.deadline = payload.deadline
    if payload.priority is not None:
        item.priority = payload.priority
    if payload.status is not None:
        item.status = payload.status
    if payload.needs_review is not None:
        item.needs_review = payload.needs_review

    await run_in_threadpool(database.save_action_item, item)

    await broadcast(meeting_id, {
        "type": "item_updated",
        "data": item.dict()
    })
    return item

@app.post("/api/meeting/{meeting_id}/items/{item_id}/confirm")
async def confirm_needs_review_item(meeting_id: str, item_id: str):
    item = database.get_action_item_by_id(meeting_id, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    item.needs_review = False
    if item.status == "needs_review":
        item.status = "pending"
    await run_in_threadpool(database.save_action_item, item)

    await broadcast(meeting_id, {
        "type": "item_updated",
        "data": item.dict()
    })
    return item

@app.post("/api/meeting/{meeting_id}/items/{item_id}/complete")
async def mark_item_complete(meeting_id: str, item_id: str):
    item = database.get_action_item_by_id(meeting_id, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    item.status = "completed"
    await run_in_threadpool(database.save_action_item, item)

    event = AgentEvent(
        id=str(uuid.uuid4())[:8],
        meeting_id=meeting_id,
        type="item_completed",
        action="STOP_REMINDERS",
        reason=f"Task '{item.task_title}' marked completed by user. Cancelling all autonomous reminders.",
        signals=["Completion signal received", "Task state: completed"],
        target=f"@{item.owner}"
    )
    await run_in_threadpool(database.save_agent_event, event)

    await broadcast(meeting_id, {
        "type": "item_completed",
        "data": {"id": item_id, "meeting_id": meeting_id}
    })
    await broadcast(meeting_id, {
        "type": "agent_event",
        "data": event.dict()
    })

    return item

@app.post("/api/meeting/upload")
async def upload_meeting(
    file: UploadFile = File(...), 
    meeting_id: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = None
):
    """Accept an audio/video recording, store it, and start processing.
    Returns a meeting_id that can be used to query status/results.
    """
    # Validate file type
    allowed_audio = {"audio/mpeg", "audio/wav", "audio/mp4", "audio/x-m4a", "audio/aac", "audio/flac", "audio/webm", "audio/ogg"}
    allowed_video = {"video/mp4", "video/quicktime", "video/x-msvideo", "video/x-matroska", "video/webm"}
    content_type = file.content_type
    if content_type not in allowed_audio.union(allowed_video):
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {content_type}")

    # Ensure upload directory exists
    upload_dir = os.path.join(os.path.dirname(__file__), "..", "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    # Generate unique meeting ID if not provided, and file path
    if not meeting_id:
        meeting_id = str(uuid.uuid4())
    file_ext = os.path.splitext(file.filename)[1]
    saved_path = os.path.join(upload_dir, f"{meeting_id}{file_ext}")
    # Save uploaded file to disk
    with open(saved_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Gather basic metadata
    file_stats = os.stat(saved_path)
    metadata: Dict = {
        "meeting_id": meeting_id,
        "file_name": file.filename,
        "file_size": file_stats.st_size,
        "content_type": content_type,
        "meeting_type": "uploaded",
    }

    # Kick off background processing
    if background_tasks is not None:
        background_tasks.add_task(process_uploaded_meeting, meeting_id, saved_path, metadata)
    else:
        await process_uploaded_meeting(meeting_id, saved_path, metadata)

    return {"meeting_id": meeting_id, "status": "processing_started"}

@app.delete("/api/meeting/{meeting_id}")
async def reset_meeting(meeting_id: str):
    scheduler.stop_agent_loop(meeting_id)
    await run_in_threadpool(database.clear_meeting_data, meeting_id)
    
    await broadcast(meeting_id, {
        "type": "meeting_reset",
        "meeting_id": meeting_id
    })
    return {"status": "reset_successful", "meeting_id": meeting_id}

from pydantic import BaseModel

class ChatQuery(BaseModel):
    query: str

@app.post("/api/chat")
async def chat_endpoint(payload: ChatQuery):
    try:
        from app.services.ai.provider_factory import get_ai_provider
        provider = get_ai_provider()
        
        # Get all meeting transcripts and topics as context
        meetings = database.get_meetings()
        context = "Meetings Content:\n"
        for m in meetings:
            topics = database.get_topics(m.id)
            topics_str = ""
            if topics:
                topics_str = "\nExtracted Topics:\n" + "\n".join([f"- {t.topic_name} ({t.start_time}-{t.end_time}): {t.summary}. Keywords: {', '.join(t.keywords)}" for t in topics])
            context += f"Meeting {m.title}:\nTranscript:\n{m.transcript}\n{topics_str}\n\n"
            
        answer = await provider.chat(context, payload.query)
        return {"answer": answer}
    except Exception as e:
        print("Chat Error:", e)
        return {"answer": f"I received your question: '{payload.query}'. However, I was unable to process it with the AI provider. Error: {str(e)}"}

# --- CALENDAR API ENDPOINTS ---

from app.models import CalendarAccount, CalendarEvent
import random

@app.get("/api/calendar/auth/{provider}")
async def calendar_auth(provider: str):
    if provider not in ["google", "outlook"]:
        raise HTTPException(status_code=400, detail="Invalid provider")
    # Stub OAuth: Return a fake auth URL
    fake_auth_url = f"/api/calendar/callback?provider={provider}&code=fake_auth_code_123"
    return {"auth_url": fake_auth_url}

@app.get("/api/calendar/callback")
async def calendar_callback(provider: str, code: str):
    if not code:
        raise HTTPException(status_code=400, detail="Missing auth code")
    
    # Save a fake account for "default_user"
    account = CalendarAccount(
        user_id="default_user",
        provider=provider,
        access_token=f"fake_{provider}_token_{uuid.uuid4()}",
        refresh_token="fake_refresh_token"
    )
    await run_in_threadpool(database.save_calendar_account, account)
    
    # Generate some fake events for testing if none exist
    events = database.get_calendar_events()
    if len(events) < 3:
        for i in range(1, 4):
            event = CalendarEvent(
                id=str(uuid.uuid4()),
                event_id=f"evt_{uuid.uuid4()}",
                title=f"Sample Meeting {i} ({provider})",
                start_time=datetime.utcnow().isoformat() + "Z",
                end_time=datetime.utcnow().isoformat() + "Z",
                participants="Alice, Bob",
                platform="Google Meet" if provider == "google" else "Teams",
                status="scheduled"
            )
            await run_in_threadpool(database.save_calendar_event, event)

    return {"status": "success", "message": f"Connected to {provider}"}

@app.get("/api/calendar/accounts")
def get_calendar_accounts():
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT provider FROM calendar_accounts WHERE user_id = 'default_user'")
    rows = cursor.fetchall()
    conn.close()
    return {"connected_providers": [r["provider"] for r in rows]}

@app.delete("/api/calendar/accounts/{provider}")
def disconnect_calendar_account(provider: str):
    database.delete_calendar_account("default_user", provider)
    return {"status": "disconnected"}

@app.get("/api/calendar/events")
def list_calendar_events():
    return database.get_calendar_events()

@app.post("/api/calendar/link/{meeting_id}/{event_id}")
def link_meeting_to_event(meeting_id: str, event_id: str):
    database.link_calendar_event(event_id, meeting_id)
    return {"status": "linked", "meeting_id": meeting_id, "event_id": event_id}

# --- SPEAKER IDENTIFICATION API ---

from app.models import SpeakerMapping
from pydantic import BaseModel

class SpeakerRename(BaseModel):
    original_speaker: str
    mapped_speaker: str

@app.get("/api/meetings/{meeting_id}/speakers")
def get_speakers(meeting_id: str):
    # Retrieve mappings
    mappings = database.get_speaker_mappings(meeting_id)
    return {"mappings": [m.dict() for m in mappings]}

@app.put("/api/meetings/{meeting_id}/speakers")
def rename_speaker(meeting_id: str, payload: SpeakerRename):
    mapping = SpeakerMapping(
        meeting_id=meeting_id,
        original_speaker=payload.original_speaker,
        mapped_speaker=payload.mapped_speaker
    )
    database.save_speaker_mapping(mapping)
    return {"status": "success", "mapping": mapping.dict()}


# --- MEETING MINUTES & EXPORT API ---

from app.models import MeetingMinute, ExportLog
from fastapi.responses import FileResponse
import tempfile
from app.services.ai.provider_factory import get_ai_provider

@app.post("/api/meetings/{meeting_id}/minutes")
async def generate_meeting_minutes(meeting_id: str):
    meeting = database.get_meeting(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
        
    provider = get_ai_provider()
    
    # Prompt for generating minutes
    prompt = """
    Generate a professional Meeting Minutes document from the following transcript.
    Format the output as clean Markdown. 
    
    Structure the document as follows:
    # Meeting Minutes: [Title]
    **Date:** (use today's date)
    **Time:** 
    **Duration:** (estimate)
    **Participants:** (list based on speakers)

    ## Executive Summary
    (A concise 2-3 sentence overview of the meeting's main purpose and overarching outcome)

    ## Key Discussion Topics
    (Organized chronologically or by theme. Bulleted highlights of what was discussed)

    ## Decisions Made
    (Explicitly documented resolutions)

    ## Action Items
    (For each item include Task, Owner, and Deadline)
    
    IMPORTANT: DO NOT OUTPUT JSON. RETURN ONLY RAW MARKDOWN TEXT.
    """
    
    try:
        response = await provider.chat(meeting.transcript, prompt)
        
        # Save generated minutes
        minute = MeetingMinute(
            meeting_id=meeting_id,
            content=response,
            format="markdown"
        )
        await run_in_threadpool(database.save_meeting_minute, minute)
        return {"status": "success", "minutes": minute.dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/meetings/{meeting_id}/minutes")
def get_meeting_minutes(meeting_id: str):
    minutes = database.get_meeting_minute(meeting_id)
    if not minutes:
        raise HTTPException(status_code=404, detail="Minutes not generated yet")
    return {"minutes": minutes.dict()}

@app.get("/api/meetings/{meeting_id}/export/{format}")
def export_meeting_minutes(meeting_id: str, format: str):
    # This is a stub for the export logic.
    # We would use reportlab for PDF, python-docx for DOCX, markdown for MD, etc.
    minutes = database.get_meeting_minute(meeting_id)
    if not minutes:
        raise HTTPException(status_code=404, detail="Minutes not generated yet")
        
    # Log export
    log = ExportLog(id=str(uuid.uuid4()), meeting_id=meeting_id, format=format)
    database.log_export(log)

    # For the stub, just return text as the requested format type
    content = minutes.content
    
    fd, path = tempfile.mkstemp(suffix=f".{format}")
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        f.write(content)
        
    media_types = {
        "pdf": "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "md": "text/markdown",
        "txt": "text/plain"
    }
    
    return FileResponse(path, media_type=media_types.get(format, "text/plain"), filename=f"Meeting_Minutes_{meeting_id}.{format}")


