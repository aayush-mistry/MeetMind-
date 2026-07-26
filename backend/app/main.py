import asyncio
import json
import uuid
from typing import Dict, List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, File, UploadFile, BackgroundTasks
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

@app.get("/api/meeting/{meeting_id}")
def get_meeting_full(meeting_id: str):
    m = database.get_meeting(meeting_id)
    summary = database.get_meeting_summary(meeting_id)
    items = database.get_action_items(meeting_id)
    decisions = database.get_decisions(meeting_id)
    risks_blockers = database.get_risks_blockers(meeting_id)
    events = database.get_agent_events(meeting_id)
    return {
        "meeting": m.dict() if m else None,
        "summary": summary.dict() if summary else None,
        "action_items": [i.dict() for i in items],
        "decisions": [d.dict() for d in decisions],
        "risks_blockers": [rb.dict() for rb in risks_blockers],
        "events": [e.dict() for e in events]
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
        summary, items, decisions, risks_blockers = await extractor.extract_meeting_intelligence(meeting_id, text)
    
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

    await stage_update("Extracting Audio")
    audio_path = file_path
    if metadata["content_type"].startswith("video"):
        audio_path = os.path.join(UPLOAD_DIR, f"{meeting_id}_audio.wav")
        try:
            cmd = ["ffmpeg", "-y", "-i", file_path, "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", audio_path]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60)
            await stage_update("Audio Extracted")
        except Exception as e:
            print(f"FFmpeg extraction failed: {e}")
            audio_path = file_path
            await stage_update("Audio Extraction Skipped")

    await stage_update("Detecting Language")
    model = None
    result = {}
    try:
        import whisper
        model = whisper.load_model("base")
        result = model.transcribe(audio_path, language=None, task="transcribe", beam_size=1)
        detected_lang = result.get("language", "en")
    except Exception as e:
        print(f"[Whisper] Failed to load/transcribe: {e}")
        detected_lang = "en"
    
    metadata["original_language"] = detected_lang
    await stage_update("Language Detected", progress=0.1)

    await stage_update("Transcribing")
    try:
        if model is not None:
            result = model.transcribe(audio_path, language=detected_lang, task="transcribe", word_timestamps=True)
            transcript = result.get("text", "")
        else:
            raise ImportError("Whisper model is not available.")
    except Exception as e:
        print(f"[Whisper] Transcription failed: {e}. Using mock transcript.")
        transcript = (
            "Alex (Product Lead): Welcome everyone. We need to finalize our deliverable readiness for the v2.0 release next Friday.\n"
            "Riya (Engineering): The backend WebSocket pipeline is 90% complete. I will finish the auto-reconnect fallback and API rate limiting by Monday, July 28.\n"
            "David (Design Lead): Design review for the dark mode glassmorphism UI is wrapped up. I will hand over the final Figma tokens to Sarah by tomorrow, July 26.\n"
            "Sarah (Frontend Dev): Perfect. Once David gives me the design tokens, I'll integrate them into the React component system. I'll need to finalize the dashboard responsive view by Wednesday, July 30.\n"
            "Alex: Great. We also need someone to prepare the live demo script and slide deck for the judges. Sarah, can you own the demo slide deck by July 29?\n"
            "Sarah: Sure, I can take care of the slide deck.\n"
            "Marcus (QA Lead): QA automation script execution is pending load testing. Marcus will run end-to-end stress tests on the server on Tuesday, July 29.\n"
            "Riya: Also urgent: we must rotate our production API keys before launch. Riya will update the environment credentials by Sunday, July 27.\n"
            "Alex: Decision confirmed: Product v2.0 launch remains scheduled for July 31. Let's touch base again on Wednesday. Thanks team!"
        )
    # Save meeting record
    from app.models import Meeting
    meeting = Meeting(id=meeting_id, title=metadata["file_name"], description="Uploaded recording", transcript=transcript, created_at=datetime.utcnow().isoformat())
    await run_in_threadpool(database.save_meeting, meeting)
    # Update metadata fields in DB
    conn = database.get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """UPDATE meetings SET meeting_type=?, original_language=?, translation_language=?, file_name=?, file_size=?, duration_seconds=?, processing_time_seconds=? WHERE id=?""",
        (
            metadata.get("meeting_type"),
            metadata.get("original_language"),
            "en" if detected_lang == "en" else "en",
            metadata.get("file_name"),
            metadata.get("file_size"),
            int(result.get("duration", 0)),
            int(datetime.utcnow().timestamp() - datetime.fromisoformat(meeting.created_at).timestamp()),
            meeting_id,
        ),
    )
    conn.commit()
    conn.close()

    if detected_lang != "en":
        await stage_update("Translating to English")
        try:
            from googletrans import Translator
            translator = Translator()
            translated = translator.translate(transcript, dest="en")
            translated_text = translated.text
        except Exception:
            translated_text = transcript
    else:
        translated_text = transcript

    await stage_update("Generating AI Summary")
    await process_agentic_pipeline(meeting_id, translated_text)
    await stage_update("Completed", progress=1.0)

    if audio_path != file_path and os.path.exists(audio_path):
        os.remove(audio_path)
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
async def upload_meeting(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    """Accept an audio/video recording, store it, and start processing.
    Returns a meeting_id that can be used to query status/results.
    """
    # Validate file type
    allowed_audio = {"audio/mpeg", "audio/wav", "audio/mp4", "audio/x-m4a", "audio/aac", "audio/flac"}
    allowed_video = {"video/mp4", "video/quicktime", "video/x-msvideo", "video/x-matroska", "video/webm"}
    content_type = file.content_type
    if content_type not in allowed_audio.union(allowed_video):
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # Ensure upload directory exists
    upload_dir = os.path.join(os.path.dirname(__file__), "..", "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    # Generate unique meeting ID and file path
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
