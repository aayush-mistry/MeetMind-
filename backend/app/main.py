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

    await stage_update("Uploading Audio to Gemini", progress=0.1)
    
    try:
        from google import genai
        import json
        client = genai.Client()
        
        # Upload the file to Gemini
        print(f"Uploading {file_path} to Gemini API...")
        uploaded_file = await run_in_threadpool(client.files.upload, file=file_path)
        
        await stage_update("Transcribing and Translating", progress=0.3)
        
        # Request transcription and language detection
        prompt = (
            "Listen to this audio file. First, identify the original spoken language. "
            "Then, transcribe the audio perfectly. If the audio is not in English, translate the transcription into English. "
            "Return a JSON object with exactly two string keys: 'original_language' and 'english_transcript'."
        )
        
        response = await run_in_threadpool(
            client.models.generate_content,
            model='gemini-1.5-flash',
            contents=[prompt, uploaded_file]
        )
        
        # Delete file from Gemini
        await run_in_threadpool(client.files.delete, name=uploaded_file.name)
        
        # Parse JSON output
        try:
            # Clean markdown code blocks if any
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            data = json.loads(text.strip())
            detected_lang = data.get("original_language", "Unknown")
            transcript = data.get("english_transcript", "")
        except Exception as e:
            print("Failed to parse Gemini JSON:", e)
            detected_lang = "Unknown"
            transcript = response.text

    except Exception as e:
        print(f"[Gemini Audio] Transcription failed: {e}")
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
async def upload_meeting(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
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

from pydantic import BaseModel

class ChatQuery(BaseModel):
    query: str

@app.post("/api/chat")
async def chat_endpoint(payload: ChatQuery):
    try:
        from google import genai
        client = genai.Client()
        
        # Get all meeting transcripts as context
        meetings = database.get_meetings()
        context = "Meeting Transcripts:\n"
        for m in meetings:
            context += f"Meeting {m.title}:\n{m.transcript}\n\n"
            
        prompt = f"Use the following meeting transcripts to answer the user's question.\n\n{context}\n\nUser Question: {payload.query}"
        
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt
        )
        return {"answer": response.text}
    except Exception as e:
        print("Chat Error:", e)
        return {"answer": f"I received your question: '{payload.query}'. However, I was unable to connect to the Gemini API to search your transcripts. Please check API keys."}

